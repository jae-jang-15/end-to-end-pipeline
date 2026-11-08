"""Orders pipeline: landing -> bronze copy and bronze -> silver cleaning (AWS Lambda).

Implementation is written in the BMAD Development stage, after the PRD and architecture
document are approved. See docs/03-architecture/adr/0002-pandas-on-lambda-instead-of-glue.md.
"""

__version__ = "0.1.0"
