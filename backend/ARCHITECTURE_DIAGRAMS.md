# System Architecture Diagrams

Use these diagrams to visualize how your Adaptive Learning Platform works. You can render these using a Mermaid viewer or online at [mermaid.live](https://mermaid.live).

## 1. Frontend Flow (User Experience)
This diagram shows how the user interacts with the website.

```mermaid
graph TD
    User([User]) -->|Opens App| Landing[Landing Page]
    Landing -->|Clicks Login| Auth[Google Login]
    Auth -->|Success| Dashboard[Dashboard]
    
    Dashboard -->|Selects Activity| Activities{Choose Activity}
    
    Activities -->|Watch Video| VideoPlayer[Video Player]
    Activities -->|Take Quiz| QuizUI[Quiz Interface]
    Activities -->|Check Stats| ProgressUI[Progress Stats]
    
    VideoPlayer -->|Request Notes| AI_Notes[View AI Notes]
    VideoPlayer -->|Watch Complete| UpdateProg[Update Progress]
    
    QuizUI -->|Submit Answers| Results[View Results]
    Results -->|Save Score| UpdateProg
    
    UpdateProg -->|Refresh Data| Dashboard
    
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Dashboard fill:#bbf,stroke:#333,stroke-width:2px
```

## 2. Backend Flow (Logic & Data)
This diagram shows how the server handles requests.

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as FastAPI Server
    participant DB as MongoDB
    participant AI as Gemini AI
    participant YT as YouTube API

    Note over Client, API: Authentication
    Client->>API: Login Request (Google Token)
    API->>API: Verify Token
    API->>DB: Create/Get User
    API-->>Client: Session Cookie (JWT)

    Note over Client, API: Video Learning
    Client->>API: Search "Python"
    API->>YT: Search Videos
    YT-->>API: Video List
    API-->>Client: Return Videos

    Client->>API: Get Notes for Video
    API->>AI: Prompt: "Summarize [Title]"
    AI-->>API: Generated Notes
    API-->>Client: Return Notes

    Note over Client, API: Progress & Quizzes
    Client->>API: Submit Quiz / Update Progress
    API->>DB: Save Results
    DB-->>API: Confirmation
    API-->>Client: Success Response
```

## 3. Combined System Architecture
This diagram shows the entire system connecting together.

```mermaid
graph LR
    subgraph Frontend [Frontend - React]
        UI[User Interface]
        State[State Management]
    end

    subgraph Backend [Backend - FastAPI]
        Router[API Router]
        AuthService[Auth Service]
        VideoService[Video Service]
        QuizService[Quiz Service]
    end

    subgraph External [External Services]
        Google[Google OAuth]
        Gemini[Gemini AI]
        YouTube[YouTube API]
    end

    subgraph Database [Data Layer]
        MongoDB[(MongoDB)]
    end

    UI <-->|HTTP Requests| Router
    
    Router --> AuthService
    Router --> VideoService
    Router --> QuizService
    
    AuthService <--> Google
    VideoService <--> YouTube
    VideoService <--> Gemini
    
    AuthService <--> MongoDB
    QuizService <--> MongoDB
    
    style Frontend fill:#e1f5fe,stroke:#01579b
    style Backend fill:#e8f5e9,stroke:#2e7d32
    style External fill:#fff3e0,stroke:#ef6c00
    style Database fill:#f3e5f5,stroke:#7b1fa2
```
