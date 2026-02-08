# Thou Art - Codebase Architecture Analysis

## 1. High-Level Architecture Summary

**Thou Art** is a full-stack cross-platform mobile application for daily affirmations. The app provides a serene, immersive experience with rotating affirmation cards, dynamic theming, and animated backgrounds.

**Architecture Type**: Client-server mobile application
- **Frontend**: Flutter app (iOS & Android) with clean architecture
- **Backend**: RESTful API with Node.js/Express
- **Database**: MongoDB with Mongoose ODM
- **State Management**: Provider pattern
- **Deployment**: Docker containerized backend

## 2. Key Modules

### Frontend (Flutter)

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **Home Feature** | Main single-screen UI with card carousel | `flutter/lib/features/home/home_page.dart` |
| **Card Carousel** | Rotating 3D card system with glassmorphic effects | `flutter/lib/features/home/widgets/card_carousel/card_carousel_controller.dart` |
| **Animated Backgrounds** | Theme-specific dynamic backgrounds | `flutter/lib/features/home/widgets/animated_backgrounds/animated_background_manager.dart` |
| **Theme System** | Dynamic theming with 5 theme options | `flutter/lib/shared/theme_provider.dart`, `flutter/lib/shared/app_themes.dart` |
| **API Service** | HTTP communication with backend | `flutter/lib/api/api_service.dart` |

### Backend (Node.js/Express)

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **Express Server** | HTTP server and middleware setup | `backend/server.js` |
| **Affirmation Controller** | Business logic for affirmation operations | `backend/controllers/affirmation.controller.js` |
| **API Routes** | RESTful endpoint definitions | `backend/routes/affirmation.routes.js` |
| **Database Seed** | Initial population with 72 affirmations | `backend/seed.js` |

## 3. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FLUTTER APP                                  │
│  ┌──────────────┐     ┌─────────────────────────────────────────┐  │
│  │ Home Page    │────▶│   Card Carousel Controller              │  │
│  │ (UI Layer)   │     │   - Manages card rotation state         │  │
│  └──────────────┘     │   - Triggers API calls on load          │  │
│         ▲             └─────────────────────────────────────────┘  │
│         │                           │                              │
│         │                           ▼                              │
│         │                  ┌────────────────┐                      │
│         │                  │  API Service   │                      │
│         │                  │  - HTTP GET    │                      │
│         │                  └────────────────┘                      │
└─────────┼───────────────────────┼──────────────────────────────────┘
          │                       │
          │ HTTP GET              │ JSON Response
          ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Express)                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Router Layer                               │   │
│  │  GET /api/v1/affirmations → affirmation.routes.js:12         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Controller Layer                             │   │
│  │  affirmation.controller.js: getRandomAffirmations()          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                Database Layer (Mongoose)                     │   │
│  │  Affirmation.aggregate([{ $sample: { size: 10 } }])          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MONGODB DATABASE                               │
│  Collections: affirmations                                          │
│  Documents: { _id, text, originalId }                               │
└─────────────────────────────────────────────────────────────────────┘
```

### State Management Flow (Provider Pattern)

1. `main.dart` initializes `MultiProvider` with `ThemeProvider` and `CardCarouselController`
2. UI widgets `Consumer<T>` listen to state changes via `ChangeNotifier`
3. Theme preferences persist via `SharedPreferences`

## 4. Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend Framework** | Flutter 3.9.2+ with Dart |
| **State Management** | Provider package |
| **Backend Runtime** | Node.js 22 |
| **Backend Framework** | Express.js 4.18.2 |
| **Database** | MongoDB 7.0.0 with Mongoose ODM |
| **Containerization** | Docker & docker-compose |
| **HTTP** | http package (Flutter), Express middleware (Node) |

## 5. API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/affirmations` | GET | Returns 10 random affirmations |
| `/` | GET | Health check |

## 6. Frontend Directory Structure

```
lib/
├── api/                    # API communication layer
│   └── api_service.dart
├── features/               # Feature-based organization
│   └── home/               # Main application feature
│       ├── widgets/
│       │   ├── animated_backgrounds/
│       │   │   ├── backgrounds/     # Individual animation implementations
│       │   │   └── animated_background_manager.dart
│       │   ├── card_carousel/       # Rotating card system
│       │   │   ├── card_carousel_controller.dart  # Business logic
│       │   │   ├── card_carousel_manager.dart      # UI management
│       │   │   ├── card_animation_state.dart       # State enum
│       │   │   └── rotation_path_painter.dart
│       │   └── settings_menu.dart
│       └── home_page.dart
└── shared/                 # Reusable components
    ├── app_themes.dart
    └── theme_provider.dart
```

## 7. Backend Directory Structure

```
backend/
├── controllers/            # Business logic
├── routes/                 # API routing
├── server.js              # Main server file
├── seed.js                # Database seeding script
├── docker-compose.yml     # Container orchestration
└── Dockerfile             # Container build instructions
```

## 8. Architectural Strengths

- **Clean Separation**: Clear division between features, shared components, and API layer
- **Scalable State Management**: Provider pattern allows for easy expansion of stateful components
- **Theme System**: Dynamic theming with persistent user preferences
- **Animation Architecture**: CustomPaint-based backgrounds providing smooth, performant animations
- **Containerized Backend**: Docker setup ensures consistent development and deployment

## 9. Areas for Potential Improvement

- **Missing Model Files**: Affirmation model appears to be missing from source control (only in node_modules)
- **Authentication**: JWT authentication planned but not yet implemented
- **Error Handling**: Basic error handling in place, could be more robust
- **Testing**: No test files visible in the codebase
- **Backend Structure**: Could benefit from more organized directory structure (middleware, services, etc.)
