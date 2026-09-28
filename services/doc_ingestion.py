from pypdf import PdfReader
import io, re

DATE_RANGE = re.compile(r"^[A-Z]{3,4}\.?\s*\d{4}\s*[–-]\s*[A-Z]{3,4}\.?\s*\d{4}$")

def clean(s):
    return re.sub(r"\s+", " ", s).strip()

def get_section(text, start_marker, end_marker=None):
    if end_marker:
        m = re.search(rf"{start_marker}\n(.*?){end_marker}", text, re.DOTALL)
    else:
        m = re.search(rf"{start_marker}\n(.*)", text, re.DOTALL)
    return m.group(1).strip("\n") if m else ""

def chunk_resume(text: str, source: str) -> list[dict]:
    chunks = []

    def add(chunk_text, section, subsection=None):
        body = chunk_text.strip()
        if not body:
            return
        prefix = f"[{source} | {section}" + (f" > {subsection}" if subsection else "") + "] "
        chunks.append({
            "text": prefix + body,
            "metadata": {"source": source, "section": section, "subsection": subsection}
        })

    # 1. Profile: name, tagline, contact info
    header = text.split("EXPERIENCE")[0]
    add(clean(header), "Profile")

    # 2. EXPERIENCE: line-based state machine.
    # A "job header" = a line containing " — " whose NEXT non-empty line is a date range.
    exp_lines = get_section(text, "EXPERIENCE", "PROJECTS").split("\n")
    i = 0
    current_company, current_dates, current_bullets = None, None, []

    def flush_job():
        if current_company and current_bullets:
            for b in current_bullets:
                add(f"At {current_company} ({current_dates}): {clean(b)}",
                    "Experience", current_company.split("—")[0].strip())

    while i < len(exp_lines):
        line = exp_lines[i].strip()
        if not line:
            i += 1
            continue
        is_job_header = "—" in line and i + 1 < len(exp_lines) and DATE_RANGE.match(exp_lines[i+1].strip())
        if is_job_header:
            flush_job()
            current_company = line
            current_dates = exp_lines[i+1].strip()
            current_bullets = []
            i += 2
            continue
        if line.startswith("●"):
            current_bullets.append(line.lstrip("●").strip())
        else:
            if current_bullets:
                current_bullets[-1] += " " + line  # wrapped continuation line
        i += 1
    flush_job()

    # 3. PROJECTS: header = a line containing ", " whose NEXT line starts with "●",
    proj_lines = get_section(text, "PROJECTS", "SKILLS").split("\n")
    i = 0
    current_project, current_bullets = None, []
    SENTENCE_END = re.compile(r"[.!?:]$")

    def flush_project():
        if current_project and current_bullets:
            for b in current_bullets:
                add(f"Project '{current_project}': {clean(b)}", "Projects", current_project)

    while i < len(proj_lines):
        line = proj_lines[i].strip()
        if not line:
            i += 1
            continue
        bullet_open = bool(current_bullets) and not SENTENCE_END.search(current_bullets[-1])
        is_project_header = (
            not bullet_open
            and not line.startswith("●")
            and ", " in line
            and i + 1 < len(proj_lines)
            and proj_lines[i+1].strip().startswith("●")
        )
        if is_project_header:
            flush_project()
            current_project = line.split(",")[0].strip()
            current_bullets = []
            i += 1
            continue
        if line.startswith("●"):
            current_bullets.append(line.lstrip("●").strip())
        else:
            if current_bullets:
                current_bullets[-1] += " " + line
        i += 1
    flush_project()

    # 4. SKILLS
    skills_lines = get_section(text, "SKILLS", "CERTIFICATIONS").split("\n")
    current_category, current_items = None, ""
    CATEGORY_LINE = re.compile(r"^([A-Za-z][A-Za-z /]*?):\s*(.*)$")

    def flush_skill():
        if current_category:
            add(f"{current_category} skills: {clean(current_items)}", "Skills", current_category)

    for line in skills_lines:
        line = line.strip()
        if not line:
            continue
        m = CATEGORY_LINE.match(line)
        if m:
            flush_skill()
            current_category, current_items = m.group(1), m.group(2)
        else:
            current_items += " " + line
    flush_skill()

    # 5. CERTIFICATIONS: alternating name / link lines
    cert_lines = [l.strip() for l in get_section(text, "CERTIFICATIONS", "EDUCATION").split("\n") if l.strip()]
    for i in range(0, len(cert_lines) - 1, 2):
        add(f"Certification: {cert_lines[i]} ({cert_lines[i+1]})", "Certifications")

    # 6. EDUCATION: "School — Degree" line followed by a date range line
    edu_lines = [l.strip() for l in get_section(text, "EDUCATION").split("\n") if l.strip()]
    i = 0
    while i < len(edu_lines):
        if "—" in edu_lines[i] and i + 1 < len(edu_lines) and DATE_RANGE.match(edu_lines[i+1]):
            add(f"{edu_lines[i]} ({edu_lines[i+1]})", "Education")
            i += 2
        else:
            i += 1

    return chunks

async def get_content(file):
    contents = await file.read()
    pdf_stream = io.BytesIO(contents)
    reader = PdfReader(pdf_stream)

    text = "\n".join(page.extract_text() for page in reader.pages)
    chunks = chunk_resume(text, file.filename)

    return {
        "filename": file.filename,
        "num_pages": len(reader.pages),
        "num_chunks": len(chunks),
        "chunks": chunks,
    }