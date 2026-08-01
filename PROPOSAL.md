# AI alliance

**Tech for Good 2026** · GDG Coimbatore · Build weekend Aug 8–9, GRD College

**Track:** AI for Sustainable Cities & Climate Action
**Team code:** TEAM-319

## Problem

Coral bleaching is often only detected once it's severe, by which point recovery is unlikely. Reef monitoring today relies on manual diver surveys and lab-based photo review, which can take up to a week to turn around, a delay confirmed by Dr. Sangamesh Uday, Project Coordinator at the Coral Reef Conservation and Research Foundation (CRCRF), Andaman & Nicobar Islands, who is supporting this project with real reef photographs.

## Who it helps

Field volunteers and reef monitors like those at CRCRF, an Andaman-based coral conservation foundation with 16 years of field experience, who currently wait on manual or lab-based photo review to know whether a reef site is bleaching..

## Solution

An AI image classifier that takes an underwater coral photo (from a diver, drone, or phone, including CRCRF-provided images), and returns a Healthy/Bleached classification with a confidence score, so a field volunteer gets an answer in seconds instead of waiting on manual review..

## Architecture

 React Web App
      ↓
Image Upload
      ↓
FastAPI Backend
      ↓
Gemini Vision API
      ↓
Bleaching Analysis
      ↓
SQLite Database
      ↓
Survey Report

## Tech stack

 React, FastAPI, Python ,Gemini API, NASA APIs, Open-Meteo API, OBIS API , PostgreSQL (or SQLite for MVP), Leaflet.js, GitHub Docker (optional)

## Getting started

1. Accept your collaborator invite (check your email / GitHub notifications).
2. Clone this repo and start building.
3. Commit early and often — this repo is what you present on the day.

---

_Created automatically when your proposal was validated._