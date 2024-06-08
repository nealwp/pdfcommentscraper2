from src.pdf import scanner


def test_parse_title():
    test_cases = [
        {
            "test": "6F: 6F - 1 of 13 Office Treatment Records - OFFCREC LIFESTREAM BEHAIVORAL CENTER Tmt. Dt.: 12/28/2016-08/30/2021 (23 pages)",
            "expected": (
                "6F",
                "6F - 1 of 13 Office Treatment Records - OFFCREC LIFESTREAM BEHAIVORAL CENTER",
                "12/28/2016",
                "08/30/2021",
            )
        },
        {
            "test": "16F: 16F - 1 of 112 Emergency Department Records - EMERREC UF HEALTH GAINESVILLE Tmt. Dt.: 01/09/2023 (17 pages)",
            "expected": (
                "16F",
                "16F - 1 of 112 Emergency Department Records - EMERREC UF HEALTH GAINESVILLE",
                "01/09/2023",
                "01/09/2023",
            )
        },
        {
            "test": "19F: 19F - 1 of 23 Medical Evidence of Record - MER VOCATIONAL REHABILITATION (12 pages)",
            "expected": (
                "19F",
                "19F - 1 of 23 Medical Evidence of Record - MER VOCATIONAL REHABILITATION",
                "",
                "",
            )
        },
    ]

    for case in test_cases:
        result = scanner.parse_title(case["test"])
        assert result == case["expected"]


def test_parse_client_info():
    expected = [
        {
            "Alleged Onset": "N/A",
            "Application": "01/01/2023",
            "Claim Type": "T16",
            "Claimant": "John Person Doe",
            "Last Change": "01/01/1970",
            "Last Insured": "N/A",
            "SSN": "000-00-0000",
        },
        {
            "Alleged Onset": "01/01/2009",
            "Application": "02/26/2022",
            "Claim Type": "T16",
            "Claimant": "Jane Person Doe",
            "Last Change": "01/01/1970",
            "Last Insured": "N/A",
            "SSN": "000-00-0000",
        }
    ]

    inputs = [
        "tests/helpers/example_page_1.txt",
        "tests/helpers/example_page_1_alt.txt"
    ]

    for i, file in enumerate(inputs):
        fd = open(file, "r")
        page_one = str(fd.read())
        result = scanner.parse_client_info(page_one)
        assert result == expected[i]
