from src.exporter.bell_summary import generate_bell_format_summary
from src.exporter.chronological_summary import generate_chronological_medical_summary
from src.exporter.tabular_summary import generate_tablular_medical_summary


def generate_summary(format, data):
    match format:
        case "Bell":
            doc = generate_bell_format_summary(data)
            return doc
        case "Tabular":
            doc = generate_tablular_medical_summary(data)
            return doc
        case "Chronological":
            doc = generate_chronological_medical_summary(data)
            return doc
        case _:
            raise Exception(f'unknown export format "{format}"')
