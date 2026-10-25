# Mobile-First Agentic Web Application Plan
**Frameworks & Tech:** Python, Django, Tailwind CSS, JavaScript, Google Antigravity SDK  
**Architecture:** Responsive, Mobile-First Progressive Web App (PWA) Ready

---

## 1. System Overview & Mobile-First Strategy

The application provides a responsive, mobile-first interface allowing users to trigger, monitor, and interact with autonomous AI agents powered by the **Google Antigravity SDK** from any device.

### Key Mobile-First Design Principles
* **Touch-Optimized UI:** Floating action buttons (FABs), bottom drawer panels, touch-friendly tap targets (minimum $48 \times 48\text{ px}$), and swipeable action cards.
* **Responsive Layout:** Tailwind CSS mobile-first grid and flexbox configuration (`block w-full sm:flex sm:w-auto`).
* **Real-time Mobile Updates:** Asynchronous WebSocket or Server-Sent Events (SSE) updates to stream agent thoughts and token execution without requiring screen refreshes or heavy data payloads.

---

## 2. Architecture & File Structure

```text
agentic_mobile_app/
│
├── config/                  # Django project settings & URL routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── agents/                  # Agentic Core Application
│   ├── services/
│   │   ├── __init__.py
│   │   └── antigravity_runner.py # Antigravity SDK wrapper & agent loops
│   ├── templates/agents/
│   │   ├── base.html        # Mobile shell template
│   │   ├── index.html       # Mobile dashboard / trigger feed
│   │   └── detail.html      # Mobile agent interaction panel
│   ├── models.py            # Task, Session, and Agent Execution logs
│   ├── urls.py              # Application endpoints
│   └── views.py             # Mobile views and API controllers
│
├── static/                  # CSS/JS Assets (Tailwind & Alpine.js/Vanilla JS)
├── manage.py
└── requirements.txt
```

---

## 3. Core Implementation Blueprint

### Step 1: Dependencies (`requirements.txt`)
```text
django>=4.2,<5.1
google-antigravity
django-environ
channels            # For mobile real-time streaming (optional/recommended)
daphne
```

---

### Step 2: Agent Integration Service (`agents/services/antigravity_runner.py`)

This service encapsulates the Antigravity agent execution loop for seamless execution within Django handlers or background tasks.

```python
import asyncio
from typing import AsyncGenerator
from google.antigravity import Agent, LocalAgentConfig

async def stream_agent_execution(prompt: str) -> AsyncGenerator[str, None]:
    """
    Executes an autonomous agent task via the Antigravity SDK
    and streams tokens for mobile presentation.
    """
    config = LocalAgentConfig(
        system_instructions=(
            "You are an autonomous agent assistant optimized for mobile presentation. "
            "Provide concise, structured, and touch-friendly markdown summaries."
        )
    )
    
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        async for token in response:
            yield token
```

---

### Step 3: Mobile View Controller (`agents/views.py`)

```python
import asyncio
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.antigravity_runner import stream_agent_execution

def mobile_dashboard(request):
    """Renders the mobile-first dashboard view."""
    return render(request, 'agents/index.html')

@csrf_exempt
def run_agent_api(request):
    """API endpoint to run agent tasks and stream output to mobile frontend."""
    if request.method == "POST":
        prompt = request.POST.get("prompt", "")
        if not prompt:
            return JsonResponse({"error": "Prompt is required"}, status=400)
            
        def event_stream():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async_gen = stream_agent_execution(prompt)
            try:
                while True:
                    token = loop.run_until_complete(async_gen.__anext__())
                    yield f"data: {token}\n\n"
            except StopAsyncIteration:
                yield "data: [DONE]\n\n"

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

    return JsonResponse({"error": "Invalid method"}, status=405)
```

---

### Step 4: Mobile Shell Template (`agents/templates/agents/base.html`)

```html
<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Antigravity Mobile Agent</title>
    <!-- Tailwind CSS CDN for rapid styling -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="h-full flex flex-col font-sans antialiased text-gray-900 selection:bg-blue-500 selection:text-white">
    
    <!-- Mobile Top Header -->
    <header class="sticky top-0 z-30 flex items-center justify-between border-b border-gray-200 bg-white/80 px-4 py-3 backdrop-blur-md">
        <h1 class="text-lg font-bold tracking-tight text-blue-600">Antigravity AI</h1>
        <span class="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Active</span>
    </header>

    <!-- Main Mobile Content Area -->
    <main class="flex-1 overflow-y-auto px-4 py-4 pb-24">
        {% block content %}{% endblock %}
    </main>

    <!-- Mobile Fixed Bottom Navigation Bar -->
    <nav class="fixed bottom-0 left-0 right-0 z-30 flex border-t border-gray-200 bg-white justify-around py-2 shadow-lg">
        <a href="#" class="flex flex-col items-center text-blue-600">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            <span class="text-xs">Agents</span>
        </a>
        <a href="#" class="flex flex-col items-center text-gray-400 hover:text-blue-600">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
            <span class="text-xs">Tasks</span>
        </a>
    </nav>
</body>
</html>
```

---

### Step 5: Mobile Interaction Dashboard (`agents/templates/agents/index.html`)

```html
{% extends 'agents/base.html' %}

{% block content %}
<div class="space-y-4">
    <!-- Prompt Input Form -->
    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <label for="prompt" class="block text-sm font-medium text-gray-700 mb-1">Trigger Agentic Workflow</label>
        <textarea id="prompt" rows="3" class="w-full rounded-lg border-gray-300 p-2 text-sm focus:border-blue-500 focus:ring-blue-500 border" placeholder="Enter instructions for the agent..."></textarea>
        <button id="submit-btn" onclick="startAgent()" class="mt-3 w-full rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white shadow hover:bg-blue-700 active:scale-[0.98] transition">
            Run Agent
        </button>
    </div>

    <!-- Live Execution Stream Output Panel -->
    <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-500 mb-2">Agent Output Stream</h2>
        <div id="output" class="min-h-[150px] rounded-lg bg-gray-50 p-3 text-sm font-mono text-gray-800 overflow-x-auto whitespace-pre-wrap">
            Awaiting task start...
        </div>
    </div>
</div>

<script>
function startAgent() {
    const prompt = document.getElementById('prompt').value;
    const outputDiv = document.getElementById('output');
    const btn = document.getElementById('submit-btn');

    if (!prompt) return;

    outputDiv.innerText = "";
    btn.disabled = true;
    btn.classList.add('opacity-50');

    const formData = new FormData();
    formData.append('prompt', prompt);

    fetch('/run-agent-api/', {
        method: 'POST',
        body: formData
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    btn.disabled = false;
                    btn.classList.remove('opacity-50');
                    return;
                }
                const chunk = decoder.decode(value);
                const lines = chunk.split("\n\n");
                lines.forEach(line => {
                    if (line.startsWith("data: ")) {
                        const token = line.replace("data: ", "");
                        if (token !== "[DONE]") {
                            outputDiv.innerText += token;
                        }
                    }
                });
                readStream();
            });
        }
        readStream();
    });
}
</script>
{% endblock %}
```

---

## 4. Execution & Testing Workflow

1. **Activate Environment & Install Requirements:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install django google-antigravity
   ```

2. **Initialize Database & Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start Mobile Dev Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   *Access `http://<your-local-ip>:8000` from your mobile device connected to the same Wi-Fi network.*