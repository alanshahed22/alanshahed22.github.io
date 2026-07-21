---
layout: post
title: "From Blog to Biometrics: Building a Health Monitor Prototype"
date: 2026-07-20 21:00:00 -0700
categories: projects
tags: [prototype, health, software, data-visualization]
---

This blog itself is brand new — set up today, actually. And the first thing worth writing about is exactly how it got here, and what's been keeping me busy leading up to it.

## Starting From Scratch

Setting up this blog took about fifteen minutes total. The stack is dead simple: [Jekyll](https://jekyllrb.com/) hosted on [GitHub Pages](https://pages.github.com/). No servers, no databases, no monthly bills. Write a markdown file, push to GitHub, it's live. That's it.

The whole thing lives in a public repo at [github.com/alanshahed22/alanshahed22.github.io](https://github.com/alanshahed22/alanshahed22.github.io). Every post is just a `.md` file in a `_posts/` folder. It's probably the lowest-friction publishing setup I've ever used, and I wanted something I'd actually stick with.

But the real reason I wanted a place to write things down is the project I've been working on.

## The Project: A Health Monitoring Prototype

Over the past few weeks I've been building a software prototype for monitoring real-time health data. The core idea: take live sensor inputs and display them cleanly so you can actually make sense of what you're looking at.

Right now the prototype tracks three vitals:

- 🌡️ **Temperature** — body or ambient, depending on sensor placement
- 🩸 **SpO2 (Blood Oxygen)** — peripheral oxygen saturation, the metric that became a household name during COVID
- ❤️ **BPM (Heart Rate)** — beats per minute, the classic

Each vital has its **own dedicated graph** that updates in real time as data comes in. No cramming everything onto one cluttered chart — each metric gets its own visual lane so you can actually read trends at a glance.

## What It Looks Like

The UI lets you manually input values for each of the three readings — useful for testing and calibration before full sensor integration. You type in a temperature, an SpO2 percentage, a BPM reading, and the corresponding graph plots it immediately.

The three graphs sit side by side (or stacked, depending on screen size), each with its own Y-axis scaled to a clinically meaningful range:

| Metric | Normal Range |
|--------|-------------|
| Temperature | 97°F – 99°F (36.1°C – 37.2°C) |
| SpO2 | 95% – 100% |
| BPM | 60 – 100 bpm |

Readings that fall outside those ranges stand out visually — the goal is to make anomalies obvious without needing to interpret raw numbers.

## Why This Matters

This prototype is a stepping stone. The end goal is a system that reads directly from sensors — wearable or otherwise — and logs, visualizes, and eventually alerts based on what it sees. But before any of that, you need a solid foundation: clean data input, reliable rendering, and a UI that doesn't get in the way.

Getting the graphing right was the interesting part. Each metric has a different update cadence, different units, and different "normal" ranges. Building them as independent components that can each be configured separately made the whole thing much easier to reason about.

## What's Next

A few things on the roadmap:

1. **Live sensor input** — replacing manual entry with real hardware readings
2. **Data logging** — saving sessions so you can review trends over time
3. **Threshold alerts** — flagging when a value goes outside the normal window
4. **Export** — CSV or JSON so the data can be used elsewhere

I'll be posting updates here as things progress. The blog was set up partly for accountability — if I write it down publicly, I have to actually ship it.

More soon.
