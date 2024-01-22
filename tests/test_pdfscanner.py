from src.pdf.scanner import parse_title


def test_parse_title():
    test_cases = [
        {
            "test": "6F: 6F - 1 of 13 Office Treatment Records - OFFCREC LIFESTREAM BEHAIVORAL CENTER Tmt. Dt.: 12/28/2016-08/30/2021 (23 pages)",
            "expected": {
                "id": "6F",
                "provider_name": "6F - 1 of 13 Office Treatment Records - OFFCREC LIFESTREAM BEHAIVORAL CENTER",
                "from_date": "12/28/2016",
                "to_date": "08/30/2021",
            }
        },
        {
            "test": "16F: 16F - 1 of 112 Emergency Department Records - EMERREC UF HEALTH GAINESVILLE Tmt. Dt.: 01/09/2023 (17 pages)",
            "expected": {
                "id": "16F",
                "provider_name": "16F - 1 of 112 Emergency Department Records - EMERREC UF HEALTH GAINESVILLE",
                "from_date": "01/09/2023",
                "to_date": "01/09/2023",
            }
        },
        {
            "test": "19F: 19F - 1 of 23 Medical Evidence of Record - MER VOCATIONAL REHABILITATION (12 pages)",
            "expected": {
                "id": "19F",
                "provider_name": "19F - 1 of 23 Medical Evidence of Record - MER VOCATIONAL REHABILITATION",
                "from_date": "",
                "to_date": "",
            }
        },
    ]

    for case in test_cases:
        result = parse_title(case["test"])
        assert result == case["expected"]
