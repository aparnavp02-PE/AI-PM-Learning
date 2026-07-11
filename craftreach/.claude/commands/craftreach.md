---
description: Generate a full Amazon India listing + 5 Gemini Imagen 2 lifestyle prompts from an artisan product image
argument-hint: [path-to-product-image]
allowed-tools: Read, Task
---

# /craftreach

You are running the **craftReach** workflow for artisan product listings.

Image to analyze: $ARGUMENTS

Steps:

1. If an image path was given in `$ARGUMENTS`, read it with the Read tool.
   If no path was given, use the most recently uploaded/attached image in
   this conversation. Never ask the user to re-upload or clarify — work with
   whatever image is available.
2. Delegate the full analysis and generation to the `craft-reach` subagent
   (via the Task tool), passing along the image so it can perform all three
   tasks:
   - 📦 Product Analysis
   - 📝 Amazon India Listing (category path, title, bullets, description,
     backend keywords, price range)
   - 🎨 5 Lifestyle Image Prompts for Google Gemini Imagen 2
3. Return the subagent's output to the user exactly as produced — with the
   exact section headers/emoji, no extra commentary, no follow-up questions.

This command never engages in back-and-forth clarification. If something is
ambiguous in the image, the craft-reach agent is instructed to make its best
inference and proceed.
