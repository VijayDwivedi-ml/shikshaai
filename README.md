## 🚀 ShikshaAI – Intent-Driven Educational Agent

### 📌 Overview

**ShikshaAI** is an AI agent built using the Google Agent Development Kit (ADK) and powered by a Gemini model. The agent is designed to **classify user intent and route requests to predefined response logic**, enabling structured lesson generation and academic question answering through a single unified interface.

The solution demonstrates how a **routing-based agent architecture** can handle diverse user inputs while maintaining clarity, consistency, and usability.

---

## 🎯 Problem Statement Alignment

This project fulfills the Track 1 requirement by:

* Building a **single AI agent** using ADK
* Leveraging a **Gemini model** for inference
* Implementing a **clearly defined capability: intent classification and request routing**
* Exposing the agent via an **HTTP endpoint**
* Accepting input requests and returning **valid structured responses**

---

## 🧠 Core Idea

The agent’s primary capability is:

> **Intent Classification → Request Routing → Structured Response Generation**

Instead of performing a single static task, the agent intelligently determines user intent and routes the request to the appropriate response logic, such as:

* Greeting interaction
* Lesson module generation
* Academic question answering

---

## ✨ Features

* **Intent Classification Engine**
  Detects user intent (greeting, lesson request, or question)

* **Dynamic Request Routing**
  Routes input to predefined response logic

* **Structured Lesson Generation**
  Produces lesson modules with:

  * Explanation
  * Classroom Activity
  * Exactly 3 Homework Questions

* **Academic Q&A Support**
  Provides clear, teacher-style explanations

* **Input Validation**
  Prompts users for missing details in structured requests

* **Multi-language Output Support**
  Generates lessons in the requested language

* **Consistent Response Formatting**
  Ensures readability and structured outputs

* **HTTP Endpoint Access**
  Enables integration and deployment

---

## 🔄 Process Flow

```text
User Request (HTTP Input)
        ↓
API Layer
        ↓
AI Agent (ADK-based)
        ↓
Intent Classification
        ↓
Decision & Routing Layer
        ↓
-----------------------------------------
|                |                      |
↓                ↓                      ↓
Greeting Logic   Lesson Generation      Q&A Logic
                 Logic                  (Answer Generation)
        ↓
Structured Response Generation
        ↓
HTTP Response Output
```

---

## 💡 Opportunities & Differentiation

Unlike traditional single-purpose agents, ShikshaAI introduces a **routing-based architecture** that dynamically adapts to user intent.

### Key Advantages:

* Eliminates need for multiple tools or modes
* Supports natural, flexible user interaction
* Ensures structured and controlled outputs

### 🌟 USP:

> **Intent-driven routing combined with structured response generation**, enabling both flexibility and consistency in educational use cases.

---

## 🛠️ Technologies Used

* **Google ADK (Agent Development Kit)** – Agent design and orchestration
* **Gemini Model** – Natural language understanding and generation
* **Python** – Core application logic
* **HTTP API Layer** – Request/response handling
* **Docker** – Containerization for deployment
* **Logging Frameworks** – Monitoring and debugging

---

## 🌐 Deployment

The agent is deployed as a containerized service and exposed via an HTTP endpoint, allowing external systems to interact with it seamlessly.

https://shiksha-ai-196385338585.us-central1.run.app

---

## 📥 Sample Input

```text
Subject: Science
Grade: 5
Topic: Photosynthesis
Language: English
```

---

## 📤 Sample Output

* Explanation of the topic
* One classroom activity
* Exactly three homework questions

---

## 🔮 Future Enhancements

* Integration with learning platforms
* Personalized lesson adaptation
* Expanded multilingual capabilities
* Enhanced evaluation and feedback mechanisms

---

## 🤝 Conclusion

ShikshaAI demonstrates how a **single AI agent** can be designed using ADK and Gemini to deliver meaningful functionality through **intent classification and intelligent routing**, while maintaining simplicity, usability, and deployment readiness.

---
