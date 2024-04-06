## Pad Station Documentation

Welcome to the Pad Station repository on GitLab! This repository manages communications, filling, and ignition of the Solaris hybrid engine. The project, written in Rust, comprises three key components: the state machine, networking, and IO control. This documentation provides a comprehensive overview of the project structure, its components, software development life cycle (SDLC), coding practices, and instructions for pull requests.

### Project Overview

The Pad Station project aims to provide a robust and reliable system for managing pre-launch operations of a hybrid rocket. It consists of three major components and the detailed documentation will be available on Nuclino:

1. **State Machine**: Manages the rocket's state during pre-launch operations, facilitating transitions between different states such as idle, filling, and ignition.

2. **Networking**: Facilitates communication between the Pad Station and other systems or controllers involved in the rocket launch process, ensuring seamless data exchange and coordination. The link between Control Station and Pad Station utilizes RFD900x and follows the packet structure defined in CHIRP. The connection between Pad Station and Rocket employs RS422, utilizing the IRIS protocol, targeting the Motor Controller CAN bus.

3. **IO Control**: Controls input and output devices connected to the Pad Station, including sensors, actuators, and interfaces with external hardware components. This includes Fill and Relief Valves, Ignitor and Quick Disconnect circuitry, temperature and battery readings. The active and pilot valve controls are actuated by a motor controller connected over the RS422 umbilical.

### Software Development Life Cycle (SDLC)

The development of the Pad Station adheres to a structured software development life cycle to ensure high-quality code and reliable performance. Our SDLC includes the following phases:

1. **Requirements Analysis**: Gather and analyze requirements from stakeholders to understand the functionality and performance expectations of the Pad Station.

2. **Design**: Architect the components of the Pad Station, including the state machine, networking protocols, and IO control mechanisms.

3. **Implementation**: Develop clean, efficient, and maintainable Rust code, following best practices and coding standards.

4. **Testing**: Conduct thorough testing of each component to verify correctness, reliability, and performance, including unit tests, integration tests, and system tests.

5. **Deployment**: Deploy the Pad Station to the target environment and perform necessary configurations or optimizations. Our target environment is Linux running on a Raspberry Pi.

6. **Maintenance**: Provide ongoing maintenance and support for the Pad Station, including bug fixes, updates, and enhancements as needed.

### Coding Practices

To ensure consistency, readability, and maintainability of the codebase, we adhere to the following coding practices:

- **Rust Usage**: Utilize Rust for its safety features, concurrency model, and performance benefits.

- **Modularization**: Divide the code into modular components for reusability and separation of concerns.

- **Descriptive Naming**: Use meaningful names for variables, functions, and modules to enhance code readability.

- **Error Handling**: Properly handle errors using Rust's Result and Option types, propagating errors to higher-level components when necessary.

- **Documentation**: Provide clear and comprehensive documentation for all code, including comments, function/method descriptions, and module-level explanations.

- **Testing**: Write extensive unit tests and integration tests to validate correctness and robustness, aiming for high code coverage to minimize the risk of bugs and regressions.

- **Git Messages:** Follow the convention outlined [here:](https://www.conventionalcommits.org/en/v1.0.0/#summary) for any commit messages. Version control is an important aspect of software development. Please include meaningful messages for any commits you make.

### Pull Request Instructions

When submitting a pull request (PR) to the Pad Station repository, please follow these guidelines:

1. **Branching**: Create a new branch for your changes based on the latest version of the `main` branch.

2. **Commit Messages**: Write clear and descriptive commit messages explaining the purpose and scope of your changes.

3. **Code Review**: Request a code review from at least one other team member and address any feedback or comments before merging the PR.

4. **Testing**: Ensure your changes pass all existing tests and consider adding new tests if necessary to cover new functionality or edge cases.

5. **Documentation**: Update relevant documentation (code comments, README, etc.) to reflect your changes if applicable.

6. **Merge**: Once your PR has been approved and all checks have passed, merge it into the `main` branch.

7. **Versioning**: If your changes introduce new features or breaking changes, update the version number following semantic versioning principles.

### Conclusion

The Pad Station repository on GitLab is a critical component of our hybrid rocket launch system. By adhering to best practices in software development, maintaining coding standards, and thorough documentation, we aim to build a reliable and efficient system for managing pre-launch operations. Feel free to reach out on Teams if you're unsure about any steps outlined above. A detailed Nuclino page covering these topics and introducing agile practices will be created in the future.