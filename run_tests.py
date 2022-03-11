import pytest
import subprocess


def generate_html_report_from_xml():
    commandline = r"C:\\Users\\samue\\AppData\\Roaming\\npm\\junit-viewer.cmd --results=reports\report.xml > reports\report.html"
    result = subprocess.run(commandline)
    return result


if __name__ == "__main__":
    retcode = pytest.main()
    generate_html_report_from_xml()
    