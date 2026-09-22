

https://github.com/user-attachments/assets/f440f466-2f50-4b51-9aed-c350ce87db13



https://github.com/user-attachments/assets/54c134bd-1432-4a70-b1bd-229def98a641



https://github.com/user-attachments/assets/170f7985-400c-4a2f-8baa-054302e6c67f

# Phrolova Desktop Pet

A lightweight AI-powered desktop pet built with PyQt5, featuring a fan-made chibi version of Phrolova from *Wuthering Waves*.

The app supports multiple movement modes, AI-powered conversations, drag-and-drop file deletion, simple animations, and other interactive features.

<img width="266" height="221" alt="Phrolova Desktop Pet Screenshot" src="https://github.com/user-attachments/assets/ffd4db47-218b-4473-be6d-488b6e802960" />

---

## ✨ Features

- 🖱️ **Three Movement Modes**
  - Follow the cursor
  - Stay in place with drag support
  - Freely wander around the screen

- 💬 **AI Chat**
  - Supports DeepSeek and other OpenAI-compatible APIs
  - Allows simple character-based conversations directly from the desktop

- 🗑️ **Drag-and-Drop File Deletion**
  - Drag a file onto the desktop pet
  - The file will be moved to the system trash
  - The character will respond after the action

- 🎨 **Character Animations**
  - Idle animation
  - Walking animation
  - Simple visual feedback for different states

- ⌨️ **Keyboard Shortcuts**
  - Press `Esc` to quickly close the chat input box or dialogue bubble

---

## 🎨 Design & Interaction

This project is not only a programming experiment, but also an exploration of desktop interaction design.

The desktop pet is designed to stay visible and interactive without taking over too much screen space. Its movement modes allow users to choose between a more active or less distracting experience depending on how they use their desktop.

The interaction system includes:

- Cursor-following behavior for active interaction
- Free roaming for a more natural desktop companion experience
- Manual dragging for direct position control
- Drag-and-drop file interaction
- Character responses after user actions
- Lightweight dialogue bubbles designed to avoid blocking the desktop
- Simple animation state changes between idle and movement

The goal was to make the character feel responsive and playful while keeping the application lightweight and unobtrusive.

---

## 📦 Installation & Usage

### 1. Requirements

- Python 3.8 or later
- macOS / Windows / Linux
- macOS is recommended and has been tested with `.app` packaging

### 2. Clone the Repository

```bash
git clone https://github.com/KennyXiang/PhrolovaDeskPet.git
cd PhrolovaDeskPet
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure AI Features (Optional)

Edit or copy `ai_config.example.json` and provide your API configuration.

The application supports APIs that follow the OpenAI-compatible interface format.

```json
{
  "api_key": "sk-your-api-key",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-v4-flash"
}
```

> **Important:** Do not upload your real API key to GitHub. Keep personal configuration files containing API keys out of version control.

If AI configuration is not provided, the chat feature will display a configuration warning. Other features such as movement, dragging, file deletion, and animations will continue to work normally.

### 5. Run the Application

```bash
python Deskpet.py
```

---

## 🕹️ Movement Modes

### Cursor Follow

The character follows the user's mouse cursor around the screen, creating a more active and responsive interaction.

### Static / Manual Dragging

The character stays in place unless manually dragged by the user. This mode is useful when users want the pet to remain visible without constantly moving around the screen.

### Free Roaming

The character moves around the desktop automatically, creating the feeling of an independent desktop companion.

---

## 💬 AI Chat

The desktop pet can connect to an OpenAI-compatible API and generate character dialogue.

Currently supported configurations include:

- DeepSeek
- Other services using an OpenAI-compatible API format

AI functionality is optional and does not affect the core desktop pet features.

---

## 🗑️ Drag-and-Drop File Deletion

Files can be dragged directly onto the desktop pet.

When a supported file is dropped onto the character:

1. The application detects the dropped file
2. The file is moved to the system trash
3. The character displays a response

For safety, files are moved to the system trash rather than being permanently deleted.

---

## 🎨 Animation

The desktop pet uses multiple image states to create simple character animations.

Current states include:

- Idle
- Walking
- Movement transitions

Example assets:

```text
images/
├── fll_still.png
├── fll_run_1.png
└── fll_run_2.png
```

Additional animation states can be added by extending the existing image and animation logic.

---

## ⌨️ Controls

| Action | Control |
|---|---|
| Move the character manually | Click and drag |
| Close chat input | `Esc` |
| Close dialogue bubble | `Esc` |
| Delete a file | Drag the file onto the desktop pet |

---

## 🗂️ Project Structure

```text
├── Deskpet.py                 # Main application
├── images/                    # Character image assets
│   ├── fll_still.png
│   ├── fll_run_1.png
│   └── fll_run_2.png
├── ai_config.example.json     # AI configuration template
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## 🔐 API Key Safety

Never store a real API key directly in a public GitHub repository.

It is recommended to keep your real configuration in a separate local file such as:

```text
ai_config.json
```

and add it to `.gitignore`.

Example:

```gitignore
ai_config.json
.env
__pycache__/
*.pyc
.DS_Store
```

Only `ai_config.example.json` should be included in the public repository.

---

## 🚧 Possible Future Improvements

- More character animations
- More interaction states
- Additional dialogue expressions
- Customizable movement behavior
- Multiple character support
- Improved settings interface
- Better cross-platform compatibility
- Local AI model support
- Additional drag-and-drop interactions

---

## 🤝 Contributing

Issues and pull requests are welcome.

Feel free to report bugs, suggest features, or propose improvements.

---

## 📄 License & Disclaimer

This project is intended for learning, personal experimentation, and non-commercial use only.

Phrolova and *Wuthering Waves* are the property of their respective copyright holders.

This project is an unofficial fan-made work and is not affiliated with, sponsored by, or endorsed by Kuro Games.

All character-related artwork and intellectual property remain the property of their respective owners.
