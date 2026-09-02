# SPECS.md

# Premium AI Voice Assistant — Product & Engineering Specification

**Version:** 1.0
**Status:** Build Specification
**Project:** Premium AI Voice Assistant
**Target Environment:** Google Antigravity
**Primary Backend:** Python + FastAPI
**Primary AI Provider:** OpenAI
**Database:** SQLite initially, with a repository abstraction for future database migration

---

# 1. PROJECT VISION

Transform the existing **LLMs Meet Speech** project into a premium, production-quality, voice-first AI assistant.

The final application should provide an experience inspired by the responsiveness and convenience of modern assistants such as Siri and futuristic assistants such as JARVIS, while maintaining a completely original:

* visual identity
* assistant name
* personality
* interface
* animations
* voice configuration
* implementation

The product must not be a superficial UI redesign.

Existing functionality must be preserved where useful and expanded into a complete AI assistant platform.

---

# 2. EXISTING PROJECT

The existing project is the starting point.

Before implementation:

1. Read `README.md`.
2. Inspect all source files.
3. Understand the current FastAPI architecture.
4. Understand the existing OpenAI integration.
5. Understand the current speech-to-text pipeline.
6. Understand the current LLM pipeline.
7. Understand the current text-to-speech pipeline.
8. Understand the existing frontend.
9. Identify reusable components.
10. Identify technical debt.
11. Identify security issues.
12. Create a migration plan.

Do not delete working functionality without a reason.

Do not rebuild the entire project blindly.

---

# 3. CORE PRODUCT

The assistant must support two primary interaction modes.

## 3.1 Text Mode

User:

```text
User types message
        ↓
Backend
        ↓
LLM
        ↓
Streaming response
        ↓
Assistant message
```

## 3.2 Voice Mode

User:

```text
User speaks
        ↓
Microphone
        ↓
Speech-to-Text
        ↓
Conversation / Memory / Tool Router
        ↓
LLM
        ↓
Response
        ↓
Text-to-Speech
        ↓
Audio playback
```

Voice mode should be the primary experience.

---

# 4. ASSISTANT STATES

The assistant must have explicit states.

Required states:

```text
IDLE
LISTENING
PROCESSING
THINKING
TOOL_USE
SPEAKING
PAUSED
ERROR
```

The frontend must visually represent the current state.

Example:

```text
IDLE
  ↓
LISTENING
  ↓
PROCESSING
  ↓
THINKING
  ↓
SPEAKING
  ↓
IDLE
```

If a tool is required:

```text
THINKING
  ↓
TOOL_USE
  ↓
THINKING
  ↓
SPEAKING
```

The state machine must not be implemented as random UI flags.

Create a centralized assistant-state model.

---

# 5. PREMIUM UI

The application must look like a premium AI product.

## Design language

Use:

* futuristic
* elegant
* minimal
* cinematic
* dark glass
* subtle gradients
* soft glow
* depth
* smooth transitions
* intelligent motion

Avoid:

* generic admin dashboards
* excessive cards
* excessive gradients
* cheap-looking neon effects
* clutter
* unnecessary animations
* huge text
* excessive borders

---

# 6. MAIN SCREEN

The main screen must contain:

## Header

Elements:

* assistant logo
* assistant name
* online/offline indicator
* current model indicator
* settings button
* conversation button
* new conversation button

---

# 7. AI CORE

The center of the application should contain a large animated AI core/orb.

The AI core is the visual identity of the application.

It must support different visual states.

## Idle

Slow breathing animation.

## Listening

The core responds to microphone input.

## Thinking

The core uses a subtle rotating/pulsing animation.

## Tool Use

Show a distinct activity state.

## Speaking

The core responds to audio amplitude/frequency when technically possible.

## Error

Use a subtle error state.

The AI core should be implemented efficiently using:

* CSS
* SVG
* Canvas
* Web Audio API

Avoid unnecessarily heavy rendering libraries.

---

# 8. VOICE WAVEFORM

Create a premium waveform/audio visualizer.

Requirements:

* microphone waveform
* speaking waveform
* smooth animation
* audio-reactive behavior where possible
* no fake "audio" animation when there is no audio input

The visualizer must reflect actual state.

---

# 9. VOICE INTERACTION

The user must be able to:

* start recording
* stop recording
* cancel recording
* see recording state
* see transcript
* submit voice input
* hear assistant response
* pause speech
* resume speech where supported
* stop speech
* replay speech

Primary button:

```text
Microphone
```

The interaction should feel immediate.

---

# 10. HANDS-FREE MODE

Add optional hands-free mode.

When enabled:

```text
listen
→ understand
→ answer
→ speak
→ return to listening
```

The user should not have to press the microphone button after every response.

Provide a clear toggle:

```text
Hands-Free Mode: ON/OFF
```

The feature must be opt-in.

---

# 11. WAKE WORD ARCHITECTURE

Create an abstraction for future wake-word support.

Example:

```text
WakeWordService
```

Do not fake wake-word detection.

If a real wake-word provider is not configured, provide:

```text
Push-to-talk mode
```

or:

```text
Hands-free mode
```

The architecture must allow a wake-word engine to be added later without rewriting the voice pipeline.

---

# 12. SPEECH-TO-TEXT

Create a provider abstraction:

```text
SpeechToTextProvider
```

Responsibilities:

* audio validation
* transcription
* language selection
* error handling
* timeout handling

The provider must not be tightly coupled to frontend code.

---

# 13. TEXT-TO-SPEECH

Create:

```text
TextToSpeechProvider
```

Responsibilities:

* voice selection
* language
* speed
* output format
* audio generation
* error handling

Never expose provider API keys to the browser.

---

# 14. VOICE SETTINGS

Create a Voice Settings panel.

Options:

```text
Voice
Language
Speech speed
Auto playback
Hands-free mode
```

Settings must persist.

Provider-specific settings must remain in the backend/service layer.

---

# 15. CONVERSATION SYSTEM

Implement persistent conversations.

Each conversation should contain:

```text
id
title
created_at
updated_at
metadata
```

Each message should contain:

```text
id
conversation_id
role
content
created_at
audio_reference
tool_metadata
```

Supported roles:

```text
user
assistant
system
tool
```

---

# 16. CONVERSATION FEATURES

Implement:

* New chat
* Rename chat
* Delete chat
* Search chats
* Open chat
* Clear messages
* Export chat
* Conversation timestamps

Conversation list should update without full page reload.

---

# 17. CHAT EXPERIENCE

Assistant messages should support:

* Markdown
* code blocks
* copy
* regenerate
* play audio
* stop audio
* retry

User messages should support:

* copy
* timestamp

Do not render arbitrary HTML unsafely.

Sanitize rendered content.

---

# 18. STREAMING

Use streaming wherever supported.

Desired flow:

```text
User
 ↓
LLM request
 ↓
Token stream
 ↓
Frontend
 ↓
Progressive rendering
```

Do not wait for the entire response before updating the UI when streaming is available.

Architecture must allow streaming TTS in the future.

---

# 19. INTERRUPTION

Users must be able to interrupt assistant speech.

Example:

```text
Assistant speaking...
        ↓
User clicks Stop
        ↓
Audio stops
        ↓
Assistant state returns to IDLE
```

In hands-free mode, a new user voice input should also be able to interrupt playback when technically supported.

---

# 20. MEMORY SYSTEM

Create an optional memory system.

Memory examples:

```text
User prefers concise answers.
User is learning Python.
User prefers Tamil responses.
```

Do not automatically save every conversation message as memory.

Memory should be selectively created.

---

# 21. MEMORY MANAGEMENT

Settings must provide:

```text
Memory: ON/OFF
```

Users can:

* view memories
* delete a memory
* clear all memories

Memory operations must be explicit and auditable.

---

# 22. PERSONALITY SYSTEM

Create assistant personality presets.

Required presets:

```text
Professional
Friendly
Concise
Tutor
Coding Assistant
Futuristic
```

Allow a custom personality.

The personality system must be implemented through configurable system instructions.

Do not hard-code personalities throughout application logic.

---

# 23. TOOL-CALLING ARCHITECTURE

Create a modular tool registry.

Example:

```python
ToolRegistry
```

Each tool must define:

```text
name
description
input_schema
execute()
```

The assistant should decide when a tool is necessary.

---

# 24. INITIAL TOOLS

Implement:

## Calculator

Example:

```text
Calculate 234 * 72
```

## Time

Example:

```text
What time is it in Tokyo?
```

## Weather

Example:

```text
What's the weather today?
```

## Web Search

Example:

```text
What happened in the news today?
```

## Notes

Allow users to create and retrieve notes.

## Reminders

Create a reminder abstraction.

## Knowledge Search

Search uploaded documents.

---

# 25. TOOL UI

When tools are used, display subtle activity.

Examples:

```text
Searching...
```

```text
Checking weather...
```

```text
Searching your knowledge base...
```

Do not expose raw API calls or internal implementation details.

After completion, return to the normal assistant state.

---

# 26. WEB SEARCH

Create a provider abstraction:

```text
WebSearchProvider
```

The assistant should only search the web when necessary.

Search results should be processed before being passed to the LLM.

Do not blindly insert arbitrary webpages into prompts.

Add:

* timeout
* result limits
* error handling
* source metadata

---

# 27. KNOWLEDGE BASE / RAG

Create a document knowledge system.

Supported files:

```text
PDF
TXT
Markdown
```

Pipeline:

```text
Upload
 ↓
Validate
 ↓
Extract text
 ↓
Chunk
 ↓
Generate embeddings
 ↓
Store vectors
 ↓
Retrieve relevant chunks
 ↓
LLM
```

---

# 28. KNOWLEDGE UI

Create a dedicated Knowledge page.

Features:

* upload document
* list documents
* search
* delete document
* file size
* upload date
* processing state
* processing errors

States:

```text
Uploading
Processing
Ready
Failed
```

---

# 29. DOCUMENT SECURITY

Restrict:

* file types
* file sizes
* filenames
* paths

Prevent:

* path traversal
* malicious filenames
* arbitrary file execution
* unauthorized file access

Temporary files must be cleaned.

---

# 30. MULTI-LANGUAGE

Support configurable languages.

Initial target languages:

```text
English
Hindi
Tamil
Spanish
French
German
```

Architecture must allow additional languages.

Separate:

```text
UI language
STT language
LLM response language
TTS language
```

---

# 31. DATABASE

Use SQLite initially.

Create proper database models.

Recommended tables:

```text
conversations
messages
settings
memories
documents
document_chunks
notes
reminders
```

Use migrations or a structured schema-management solution.

Do not put SQL queries throughout API route files.

---

# 32. REPOSITORY LAYER

Where appropriate create repositories:

```text
ConversationRepository
MessageRepository
MemoryRepository
DocumentRepository
SettingsRepository
```

Business logic belongs in services.

Routes should remain thin.

---

# 33. BACKEND STRUCTURE

Recommended architecture:

```text
app/
├── main.py
├── config.py
│
├── api/
│   ├── chat.py
│   ├── voice.py
│   ├── conversations.py
│   ├── memories.py
│   ├── knowledge.py
│   ├── settings.py
│   └── tools.py
│
├── services/
│   ├── llm/
│   ├── speech/
│   ├── conversation/
│   ├── memory/
│   ├── rag/
│   ├── tools/
│   └── search/
│
├── database/
│   ├── models.py
│   ├── session.py
│   └── repositories/
│
├── schemas/
│
├── utils/
│
└── static/
```

Adapt this structure to the existing project rather than forcing it unnecessarily.

---

# 34. API

Implement clean API routes.

Suggested endpoints:

```text
GET    /health

POST   /api/chat

POST   /api/voice/transcribe
POST   /api/voice/synthesize

GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}
PATCH  /api/conversations/{id}
DELETE /api/conversations/{id}

GET    /api/settings
PATCH  /api/settings

GET    /api/memories
POST   /api/memories
DELETE /api/memories/{id}

POST   /api/knowledge/upload
GET    /api/knowledge/documents
DELETE /api/knowledge/documents/{id}

GET    /api/tools
POST   /api/tools/execute

GET    /api/notes
POST   /api/notes
PATCH  /api/notes/{id}
DELETE /api/notes/{id}

GET    /api/reminders
POST   /api/reminders
DELETE /api/reminders/{id}
```

Use Pydantic request/response schemas.

---

# 35. CONFIGURATION

Use environment variables.

Create:

```text
.env.example
```

Never commit:

```text
API keys
tokens
passwords
private credentials
```

Example categories:

```text
OPENAI_API_KEY
DATABASE_URL
APP_ENV
LOG_LEVEL
```

Provider configuration must remain server-side.

---

# 36. SECURITY

Implement:

* request validation
* upload validation
* file-size limits
* safe filenames
* path traversal protection
* safe HTML rendering
* API-key protection
* safe error responses
* temporary-file cleanup
* reasonable request limits
* input sanitization
* secure configuration handling

Never return raw exception traces to normal users.

---

# 37. ERROR STATES

Every operation must have a defined failure state.

Examples:

```text
Microphone permission denied
Microphone unavailable
Speech recognition failed
AI request failed
Speech synthesis failed
Network unavailable
Tool failed
Document processing failed
Database failure
```

The UI must never remain permanently stuck in:

```text
Thinking...
```

or:

```text
Speaking...
```

after an error.

---

# 38. LOADING STATES

Create polished loading states.

Examples:

```text
Listening...
Thinking...
Searching...
Reading document...
Generating response...
Speaking...
```

Use the assistant core and waveform rather than generic spinners whenever possible.

---

# 39. SETTINGS

Create a complete Settings page.

Sections:

## General

* theme
* interface language
* animations

## AI

* model
* personality
* response length

## Voice

* voice
* language
* speed
* auto-play

## Memory

* enabled/disabled
* memory management

## Privacy

* stored conversations
* stored audio
* clear local data

## About

* application version
* project information

---

# 40. THEMING

Support:

```text
Dark
Light
System
```

Persist theme preference.

Animations should respect:

```text
prefers-reduced-motion
```

---

# 41. ACCESSIBILITY

Implement:

* keyboard navigation
* focus states
* semantic HTML
* accessible labels
* sufficient contrast
* screen-reader-friendly controls
* reduced motion support

Microphone controls must have accessible labels.

---

# 42. RESPONSIVE DESIGN

Support:

```text
Desktop
Laptop
Tablet
Mobile
```

Mobile layout should not simply shrink the desktop layout.

Create an intentional mobile experience.

---

# 43. PERFORMANCE

Optimize:

* frontend bundle size
* API calls
* database queries
* audio handling
* document processing
* streaming
* conversation loading

Use asynchronous processing where appropriate.

Do not block the FastAPI event loop with heavy operations.

---

# 44. LOGGING

Create structured application logging.

Log:

* request failures
* provider errors
* tool failures
* document processing failures
* important system events

Never log:

* API keys
* passwords
* sensitive user secrets

---

# 45. TESTING

Create backend tests for:

```text
health
chat
validation
conversations
messages
settings
memory
documents
tools
notes
reminders
error handling
```

Test important service-layer logic independently.

---

# 46. FRONTEND TESTING

Verify:

* page loading
* chat
* microphone UI
* recording states
* assistant states
* conversation sidebar
* settings
* theme
* knowledge base
* responsive layout
* error states

---

# 47. BROWSER TESTING

Antigravity must actually launch the application and interact with it through the browser.

Verify:

1. Application starts.
2. Main page loads.
3. New conversation works.
4. Text message works.
5. Assistant response renders.
6. Voice UI is accessible.
7. Settings opens.
8. Theme changes.
9. Conversation history works.
10. Mobile viewport works.
11. No major console errors.
12. No broken network requests.

Do not claim browser testing was completed unless it was actually performed.

---

# 48. UI QUALITY STANDARD

Before declaring completion, inspect the application visually.

Ask:

* Does this look like a premium AI product?
* Does it feel cohesive?
* Are animations smooth?
* Are controls obvious?
* Is the interface too cluttered?
* Does the AI core look polished?
* Does mobile look intentional?
* Are empty states attractive?
* Are errors understandable?
* Does the voice interaction feel central?

If the answer is no, improve the UI.

---

# 49. ORIGINAL VISUAL IDENTITY

Do not reproduce:

* Siri UI
* Apple branding
* Iron Man/JARVIS exact branding
* copyrighted logos
* proprietary character visuals

Instead create an original assistant identity.

Use a configurable assistant name.

Default example:

```text
NOVA
```

The name must be easy to change later.

---

# 50. PREMIUM DETAILS

Add subtle high-quality details:

* command palette
* keyboard shortcuts
* animated status indicators
* conversation search
* copy buttons
* response regeneration
* audio controls
* smooth sidebar transitions
* toast notifications
* skeleton loading
* empty states
* connection status
* model indicator
* tool activity indicators

Do not add features simply to increase the feature count.

Every feature must improve usability.

---

# 51. KEYBOARD SHORTCUTS

Suggested:

```text
Ctrl/Cmd + K
Command palette

Ctrl/Cmd + N
New conversation

Ctrl/Cmd + /
Focus chat input

Esc
Stop/cancel active operation
```

Document shortcuts in the UI.

---

# 52. COMMAND PALETTE

Create a command palette for power users.

Example actions:

```text
New conversation
Search conversations
Open settings
Toggle voice mode
Toggle hands-free
Clear conversation
Open knowledge base
Change theme
```

---

# 53. NOTIFICATIONS

Use non-intrusive toast notifications.

Examples:

```text
Conversation deleted
Settings saved
Document uploaded
Memory removed
Voice unavailable
```

Avoid excessive notifications.

---

# 54. PRIVACY CONTROLS

Users must be able to control storage.

Provide options for:

```text
Save conversations
Save audio
Save memories
```

The UI must clearly explain what each option means.

---

# 55. AUDIO STORAGE

Do not permanently store generated audio unless necessary.

Prefer temporary storage where possible.

If audio persistence is implemented:

* make it configurable
* associate it with the correct message
* clean orphaned files
* provide deletion controls

---

# 56. PROVIDER ABSTRACTIONS

Avoid coupling the application directly to one implementation.

Create interfaces/abstractions for:

```text
LLMProvider
SpeechToTextProvider
TextToSpeechProvider
EmbeddingProvider
WebSearchProvider
```

OpenAI can be the first implementation.

---

# 57. FUTURE EXTENSIBILITY

Architecture should make it possible to add:

* local LLMs
* additional TTS providers
* additional STT providers
* additional vector databases
* additional web-search providers
* authentication
* cloud deployment
* mobile application
* desktop application

without rewriting the core assistant.

---

# 58. CODE QUALITY

Follow:

* clean naming
* small functions
* separation of concerns
* type hints
* Pydantic validation
* async where appropriate
* clear documentation
* reusable components

Avoid:

* giant functions
* giant files
* duplicated logic
* hard-coded configuration
* magic values
* unnecessary abstractions

---

# 59. DEPENDENCIES

Only add dependencies when justified.

For every new dependency:

1. Explain why it is needed.
2. Prefer mature packages.
3. Avoid duplicate functionality.
4. Update requirements.
5. Verify installation.
6. Run tests afterward.

---

# 60. MIGRATION STRATEGY

Do not attempt a destructive rewrite in one step.

Use phases:

```text
Phase 1
Audit

Phase 2
Backend refactor

Phase 3
Database

Phase 4
Conversation system

Phase 5
Premium frontend

Phase 6
Voice improvements

Phase 7
Streaming

Phase 8
Memory

Phase 9
Tools

Phase 10
RAG

Phase 11
Settings

Phase 12
Testing

Phase 13
Browser verification

Phase 14
Documentation
```

After every major phase:

* run tests
* fix failures
* verify application startup

---

# 61. DEFINITION OF DONE

The project is complete only when all of the following are true:

## Core

* [ ] Application starts
* [ ] Existing text functionality works
* [ ] Voice transcription works
* [ ] AI response works
* [ ] TTS works
* [ ] Audio playback works

## UI

* [ ] Premium visual design
* [ ] AI core
* [ ] Waveform
* [ ] Assistant states
* [ ] Responsive layout
* [ ] Dark/light/system theme
* [ ] Mobile experience

## Conversations

* [ ] Persistent chats
* [ ] New chat
* [ ] Rename
* [ ] Delete
* [ ] Search
* [ ] Export

## Voice

* [ ] Recording
* [ ] Transcription
* [ ] TTS
* [ ] Stop speaking
* [ ] Replay
* [ ] Voice settings
* [ ] Hands-free mode

## AI

* [ ] Personality
* [ ] Memory
* [ ] Streaming architecture
* [ ] Tool system
* [ ] Web search
* [ ] Knowledge base

## Data

* [ ] SQLite
* [ ] Repository architecture
* [ ] Document storage
* [ ] Memory storage
* [ ] Settings persistence

## Security

* [ ] API keys protected
* [ ] File validation
* [ ] Request validation
* [ ] Safe errors
* [ ] Path traversal protection

## Quality

* [ ] Tests pass
* [ ] Browser testing complete
* [ ] No major console errors
* [ ] README updated
* [ ] `.env.example` updated

---

# 62. FINAL REPORT

After implementation, create:

```text
IMPLEMENTATION_REPORT.md
```

Include:

## 1. Summary

What was built.

## 2. Features

Every major feature implemented.

## 3. Architecture

Final architecture.

## 4. Files

Files created and modified.

## 5. Dependencies

New dependencies and reasons.

## 6. Database

Schema and migrations.

## 7. API

Endpoints added/modified.

## 8. Testing

Tests executed and results.

## 9. Browser Verification

Pages and flows tested.

## 10. Known Limitations

Be honest about anything unavailable.

## 11. Run Instructions

Exact commands required to start the application.

---

# 63. ANTIGRAVITY EXECUTION RULE

This file is the authoritative specification.

Antigravity should:

1. Read this file.
2. Read the existing README.
3. Inspect the complete repository.
4. Create an implementation plan.
5. Implement the plan.
6. Run tests.
7. Launch the application.
8. Perform browser testing.
9. Fix discovered issues.
10. Perform a final visual quality review.
11. Update documentation.
12. Create `IMPLEMENTATION_REPORT.md`.

Do not stop after planning.

Do not merely generate recommendations.

Do not leave major features as fake placeholders.

Build the working application.

---

# 64. QUALITY BAR

The final result should feel like:

> "A real premium AI voice assistant product."

Not:

> "A student demo with a fancy background."

Prioritize:

```text
Reliability
+
Responsiveness
+
Voice UX
+
Visual polish
+
Clean architecture
+
Extensibility
+
Security
```

over simply maximizing the number of features.

---

# END OF SPECIFICATION
