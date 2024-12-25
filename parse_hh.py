import requests
from bs4 import BeautifulSoup


def get_html(url: str):
    return requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        },
    )


def safe_find(soup, selector, attribute=None, default="N/A"):
    try:
        element = soup.select_one(selector)
        return element[attribute].strip() if attribute else element.text.strip()
    except (AttributeError, TypeError):
        return default


def extract_vacancy_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Извлекаем текст из <h1> элемента
    h1_element = soup.find('h1', {'data-qa': 'title'})

    # Получаем объединённый текст
    title = ''.join(h1_element.stripped_strings)
    salary = safe_find(soup, 'span[data-qa="vacancy-salary-compensation-type-net"]')
    experience = safe_find(soup, 'span[data-qa="vacancy-experience"]')
    employment_mode = safe_find(soup, 'p[data-qa="vacancy-view-employment-mode"]')
    company = safe_find(soup, 'a[data-qa="vacancy-company-name"]')
    location = safe_find(soup, 'p[data-qa="vacancy-view-location"]')
    description = safe_find(soup, 'div[data-qa="vacancy-description"]')
    skills = [
        skill.text.strip()
        for skill in soup.select('li[data-qa="skills-element"]')
    ]

    # Формирование строки в формате Markdown
    markdown = f"# {title}\n\n"
    markdown += f"**Компания:** {company}\n\n"
    markdown += f"**Зарплата:** {salary}\n\n"
    markdown += f"**Опыт работы:** {experience}\n\n"
    markdown += f"**Тип занятости и режим работы:** {employment_mode}\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += "## Описание вакансии\n\n"
    markdown += f"{description}\n\n"
    markdown += "## Ключевые навыки\n\n"
    if skills:
        markdown += "- " + "\n- ".join(skills) + "\n"
    else:
        markdown += "*Навыки не указаны*\n"

    return markdown


def extract_candidate_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Извлечение основных данных кандидата
    name = safe_find(soup, 'h2[data-qa="bloko-header-1"]')
    gender_age = safe_find(soup, 'p')
    location = safe_find(soup, 'span[data-qa="resume-personal-address"]')
    job_title = safe_find(soup, 'span[data-qa="resume-block-title-position"]')
    job_status = safe_find(soup, 'span[data-qa="job-search-status"]')

    # Извлечение опыта работы
    experience_section = soup.find('div', {'data-qa': 'resume-block-experience'})
    experiences = []
    if experience_section:
        experience_items = experience_section.find_all('div', class_='resume-block-item-gap')
        for item in experience_items:
            period = safe_find(item, 'div.bloko-column_s-2')
            duration = safe_find(item, 'div.bloko-text')
            if duration != "N/A":
                period = period.replace(duration, f" ({duration})")

            company = safe_find(item, 'div.bloko-text_strong')
            position = safe_find(item, 'div[data-qa="resume-block-experience-position"]')
            description = safe_find(item, 'div[data-qa="resume-block-experience-description"]')
            experiences.append(f"**{period}**\n\n*{company}*\n\n**{position}**\n\n{description}\n")

    # Извлечение ключевых навыков
    skills_section = soup.find('div', {'data-qa': 'skills-table'})
    skills = []
    if skills_section:
        skills = [skill.text.strip() for skill in skills_section.find_all('span', {'data-qa': 'bloko-tag__text'})]

    # Формирование строки в формате Markdown
    markdown = f"# {name}\n\n"
    markdown += f"**{gender_age}**\n\n"
    markdown += f"**Местоположение:** {location}\n\n"
    markdown += f"**Должность:** {job_title}\n\n"
    markdown += f"**Статус:** {job_status}\n\n"
    markdown += "## Опыт работы\n\n"
    if experiences:
        for exp in experiences:
            markdown += exp + "\n"
    else:
        markdown += "*Опыт работы не указан*\n\n"
    markdown += "## Ключевые навыки\n\n"
    if skills:
        markdown += ', '.join(skills) + "\n"
    else:
        markdown += "*Навыки не указаны*\n"

    return markdown


def get_candidate_info(url: str):
    response = get_html(url)
    return extract_candidate_data(response.text)


def get_job_description(url: str):
    response = get_html(url)
    return extract_vacancy_data(response.text)
