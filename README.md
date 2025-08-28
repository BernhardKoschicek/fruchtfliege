# Fruchtfliege – Vienna City Fly Presentation Site

Welcome to **Fruchtfliege**! This repository hosts the presentation site for the **Vienna City Fly 2024** citizen science project using a Python 3 Dash application. It also includes a Dockerfile for easy deployment and integration.

##  Project Overview

**Vienna City Fly 2024** is a citizen science project developed under the **FAIRiCUBE** initiative funded by Horizon Europe. The goal is to harness the help of volunteers across Vienna to collect and study the genetic diversity of *Drosophila melanogaster* (fruit flies) in urban environments from April to October 2024 ([Project Website](https://freunde.nhm-wien.ac.at/neuigkeiten/item/299-vienna-city-fly-2024)).

Key objectives include:

- Collecting *D. melanogaster* samples in home kitchens.
- Sequencing up to 100 fly populations.
- Collaborating with FAIRiCUBE partners in Luxembourg to analyze genomic data alongside high‑resolution environmental and climate data ([Project Website](https://freunde.nhm-wien.ac.at/neuigkeiten/item/299-vienna-city-fly-2024)).
- Investigating whether geographic barriers like the Danube or urban environmental stressors (e.g., heat islands, sealed surfaces) affect genetic diversity or indicate signatures of adaptation ([Project Website](https://freunde.nhm-wien.ac.at/neuigkeiten/item/299-vienna-city-fly-2024)).
- Raising awareness and participation through aspects like Citizen Science Day, ECSA Conference, and the Long Night of Research ([Project Website](https://freunde.nhm-wien.ac.at/neuigkeiten/item/299-vienna-city-fly-2024)).

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Usage](#usage)
- [Docker](#docker)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Interactive Presentation**: A sleek Dash-based interface showcasing the Vienna City Fly project.
- **Modular and Extensible**: Designed for easy updates and enhancements.
- **Containerized Setup**: Ready to run via Docker for consistent environments and swift deployment.

## Tech Stack

| Component         | Description                          |
|------------------|--------------------------------------|
| **Python 3**     | Core programming language            |
| **Dash**         | Web application framework            |
| **Docker**       | Containerization for deployment      |

## Usage

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/BernhardKoschicek/fruchtfliege.git
   cd fruchtfliege
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Dash application:
   ```bash
   python runserver.py
   ```

4. Open your browser and navigate to: `http://127.0.0.1:8050`

---

## Docker

To launch the app within a containerized environment:

```bash
docker build -t fruchtfliege .
docker run -d -p 8050:8050 fruchtfliege
```

Then visit `http://localhost:8050` in your browser.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Vienna City Fly 2024** — Citizen Science initiative under the **FAIRiCUBE** project (Horizon Europe) ([Project Website](https://freunde.nhm-wien.ac.at/neuigkeiten/item/299-vienna-city-fly-2024)).
- All participating citizen scientists across Vienna.
- Project collaborators and hosting platform.
