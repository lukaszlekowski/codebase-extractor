# Thou Art - Daily Affirmations (Mobile)

This project is a full-stack daily affirmations app built for iOS and Android using:

- **Frontend (Mobile App):** Flutter, Dart, Provider (for state management)
- **Backend:** Node.js, Express, Mongoose
- **Database:** MongoDB
- **Authentication:** Logto (planned, currently manual JWT validation in backend)
- **Containerization:** Docker (for backend and database)

## Project Overview

### Purpose

To provide a serene and immersive native mobile experience (iOS & Android) for users to engage with daily affirmations. The application is designed as a tool for mindfulness and positive reinforcement, offering a focused, distraction-free environment to help users cultivate a positive mindset, gain mental clarity, and start their day with intention.

### Vision

To be a personal sanctuary where users can find a moment of peace and introspection on their mobile devices. The experience aims to feel tranquil and meditative, blending beautiful, customizable aesthetics (themes and sounds) with a core mechanic of mindful choice.


# Docs index

## What goes where
- specs/: Stable requirements (PRDs). Rarely edited after acceptance.
- research/: Facts-only snapshots used to create a plan. Date-stamped; may go stale.
- plans/: Execution contracts. Must include verification commands and "done means" checks. Archive when finished.
- adr/: Architecture decisions (why we chose X over Y). Numbered, append-only, may be superseded.

## Workflow (RPI)
1) Research → create a research doc in docs/research/
2) Plan → create a plan doc in docs/plans/ that references the research doc
3) Implement → follow the plan phase-by-phase; run verification after each phase; update checkboxes
4) If reality differs → update the plan (iterate) and continue

## Conventions
- Research/Plan filenames: YYYY-MM-DD-HHmm-<slug>.md
- ADR filenames: NNNN-<slug>.md

## Prerequisites

- **Flutter SDK:** [Install Guide](https://docs.flutter.dev/get-started/install)
- **Xcode** (for iOS development on macOS)
- **Android Studio** (for Android development, includes Android SDK)
- **Docker & Docker Compose** (for running the backend)
- **Code Editor:** VS Code with the Flutter extension is recommended.

## Setup

1.  **Clone Repositories:**

    ```bash
    git clone [https://github.com/lukaszlekowski/thou-art-flutter.git](https://github.com/lukaszlekowski/thou-art-flutter.git) flutter
    git clone [https://github.com/lukaszlekowski/thou-art-backend.git](https://github.com/lukaszlekowski/thou-art-backend.git) backend
    # Place both folders inside a common parent directory (e.g., 'thou-art/')
    ```

2.  **Backend Setup:**

    - Navigate to the `backend` directory: `cd backend`
    - Create a `.env` file (copy `.env.example` if available) and fill in your MongoDB URI, Logto details (even if using manual validation now), session secret, etc.
    - Run the backend using Docker: `docker-compose up -d --build`
    - Seed the database (if needed): `docker-compose exec backend node seed.js`
    - Backend API will be available at `http://localhost:4000`.

3.  **Flutter App Setup:**
    - Navigate to the `flutter` directory: `cd ../flutter`
    - Install dependencies: `flutter pub get`
    - **Crucially:** Ensure the API base URL in `lib/api/api_service.dart` is correct for your simulator/emulator (`http://127.0.0.1:4000` for iOS Sim, `http://10.0.2.2:4000` for Android Emu).
    - Open the project in VS Code: `code .`
    - Select your target device (iOS Simulator or Android Emulator) in VS Code (bottom-right).
    - Run the app: Press `F5` or use the "Run and Debug" panel.

## Project Structure

- `backend/`: Contains the Node.js/Express backend API.
- `flutter/`: Contains the Flutter mobile application.

_(See `AI_GUIDE.md` for more detailed architecture)_
