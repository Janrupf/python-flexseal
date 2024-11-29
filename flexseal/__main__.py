import logging
from flexseal.pip.install_report import InstallReport
from flexseal.pip.models import InstallReportModel
from flexseal.sealed import SealedInstallInstructions
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="python-flexseal",
        description="Generate a reproducible lock file from python package installations",
        epilog="This has been programming in 3 hours, bad code ahead"
    )

    parser.add_argument("-p", "--pip-install-report", type=str, required=True, help="Path to the pip install report")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the output file")

    args = parser.parse_args()
    install_report_file = args.pip_install_report
    output_file = args.output

    logging.basicConfig(format="[%(levelname)s] %(asctime)s - %(message)s", level=logging.DEBUG)

    with open(install_report_file, "r") as report_file:
        report = InstallReport(InstallReportModel.model_validate_json(report_file.read()))

    required_packages = set()
    queued_packages = list()

    for package in report.explicit_packages():
        logging.info(f"Queuing explicit package {package}")
        queued_packages.append(package)
        required_packages.add(package)

    step = 0
    while len(queued_packages) > 0:
        step += 1
        logging.info(f"Step {step}")
        for package in queued_packages:
            logging.info(f"Processing package {package}")
            for dependency in report.dependencies_of(package):
                if dependency not in required_packages:
                    logging.info(f"Queuing dependency {dependency}")
                    required_packages.add(dependency)
                    queued_packages.append(dependency)

            queued_packages.remove(package)

    logging.info(f"Finished processing after step {step}")
    logging.info(f"{len(required_packages)} packages required")

    all_packages = report.all_packages()
    for package in all_packages:
        if package not in required_packages:
            logging.warning(f"Package {package} was installed but is not required?")

    sealed_required_packages = list(map(report.seal, required_packages))

    sealed_instructions = SealedInstallInstructions.model_construct(
        packages=sealed_required_packages
    )

    with open(output_file, "w") as instructions_file:
        instructions_file.write(sealed_instructions.model_dump_json(indent=2))


if __name__ == "__main__":
    main()