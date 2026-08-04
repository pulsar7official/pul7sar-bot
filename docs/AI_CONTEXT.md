# PUL7SAR AI CONTEXT

> This document is the primary context file for every AI assistant working on the PUL7SAR project.
> Read this file completely before making any code changes.

---

# Project Name

PUL7SAR

---

# Project Vision

PUL7SAR is a premium global sports media platform focused on football first, with future expansion to all major sports.

The objective is NOT to build a Telegram bot.

The Telegram bot is only the first publishing client.

The long-term goal is to build one central content engine capable of publishing to:

- Telegram
- Facebook
- Instagram
- X (Twitter)
- TikTok
- YouTube
- Website
- Future Mobile App

Every engineering decision must support this long-term vision.

---

# Current Project Status

Current production system:

- Telegram Bot is operational.
- GitHub Actions automation is working.
- AI-generated sports news is already published.
- Automatic scheduling is already configured.
- Existing production bot MUST remain stable.

The production bot is considered stable.

Do NOT rewrite it unless explicitly requested.

---

# Current Development Phase

Current Sprint:

Visual Engine Version 2

This is a completely independent module.

It MUST NOT modify the production Telegram bot until fully completed and tested.

---

# Visual Engine Mission

The Visual Engine is responsible only for creating premium sports graphics.

Its purpose is to replace the current image generation system with a professional, scalable engine.

The engine must generate cards without depending on manual design.

---

# Brand Identity

Brand Name:

PUL7SAR

Identity:

Premium

Modern

Athletic

Fast

Global

Professional

Visual language:

Dark stadium atmosphere

Dynamic lighting

Premium typography

Strong hierarchy

Minimal clutter

High readability

---

# Primary Brand Colors

Main Accent:

Chelsea Blue

Dark Backgrounds

Metallic Silver Typography

Red is reserved ONLY for special situations and brand accents.

Blue is the default identity color.

---

# Design Philosophy

Every generated image must immediately feel like PUL7SAR.

Avoid generic templates.

Avoid social-media cliché designs.

Designs must look like premium sports broadcasters.

---

# Architecture

The project follows the standalone Visual Engine v2 architecture.

Templates describe layouts.

Renderer creates pixels.

Reusable logic must never be duplicated.

Every component must have a single responsibility.

---

# Current Engineering Rules

Never break the production bot.

Never duplicate code.

Never hardcode colors.

Never hardcode fonts.

Never hardcode dimensions.

Configuration must live in configuration files.

Templates must stay reusable.

---

# AI Working Rules

Before writing code:

1. Read this file.
2. Read ARCHITECTURE.md.
3. Read TASKS.md.

Only then begin implementation.

---

# Current Priority

Highest Priority:

Build Visual Engine v2.

Everything else is secondary.

---

# Current Objective

Create the best AI-powered sports visual engine possible.

Quality is always more important than speed.

---

# Last Updated

Version 1.0
