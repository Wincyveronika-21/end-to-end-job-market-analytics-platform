"""
Skill Taxonomy for NLP skill extraction from job postings.
Categorizes tech skills into Programming, Data Analytics, Cloud/DevOps, AI/ML, Databases, Frameworks, and Tools.
"""

SKILL_TAXONOMY = {
    "Programming": [
        "python", "sql", "java", "c++", "c#", "javascript", "typescript",
        "go", "golang", "rust", "scala", "r", "php", "ruby", "swift", "kotlin", "bash", "powershell"
    ],
    "Data & Analytics": [
        "power bi", "tableau", "excel", "pandas", "numpy", "scikit-learn",
        "spark", "apache spark", "pyspark", "hadoop", "dbt", "airflow",
        "snowflake", "databricks", "looker", "sas", "spss", "statistica",
        "data warehousing", "etl", "business intelligence", "data modeling"
    ],
    "Databases": [
        "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis",
        "oracle", "sql server", "mssql", "dynamodb", "cassandra", "elasticsearch",
        "neo4j", "cockroachdb", "bigquery"
    ],
    "Cloud & DevOps": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "docker", "kubernetes", "k8s", "terraform", "ansible", "ci/cd",
        "jenkins", "github actions", "gitlab", "linux", "unix"
    ],
    "AI & Machine Learning": [
        "machine learning", "deep learning", "pytorch", "tensorflow", "keras",
        "nlp", "natural language processing", "computer vision", "llm",
        "genai", "generative ai", "langchain", "transformers", "huggingface",
        "neural networks", "xgboost"
    ],
    "Frameworks & Web": [
        "react", "react.js", "angular", "vue", "vue.js", "node.js", "express",
        "fastapi", "django", "flask", "spring boot", "dot net", ".net", "next.js"
    ],
    "Methodologies & Soft Skills": [
        "agile", "scrum", "jira", "git", "communication", "problem solving",
        "leadership", "project management", "a/b testing"
    ]
}

# Mapping canonical names to avoid duplicates (e.g. 'postgres' -> 'PostgreSQL')
CANONICAL_SKILLS = {
    "power bi": "Power BI",
    "tableau": "Tableau",
    "python": "Python",
    "sql": "SQL",
    "r": "R",
    "excel": "Excel",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "pyspark": "PySpark",
    "scikit-learn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "react.js": "React",
    "node.js": "Node.js",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "airflow": "Apache Airflow",
    "dbt": "dbt",
    "llm": "LLMs",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "git": "Git",
    "linux": "Linux",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "c#": "C#",
    "golang": "Go",
    "go": "Go",
    "rust": "Rust"
}

def get_skill_category(skill_canonical_name: str) -> str:
    """Returns the primary category for a canonical skill name."""
    skill_lower = skill_canonical_name.lower()
    for cat, list_of_skills in SKILL_TAXONOMY.items():
        if any(s.lower() == skill_lower for s in list_of_skills):
            return cat
    return "Other Tech"
