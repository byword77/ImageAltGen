# ImageAltGen
Sigil Plugin for Automated EPUB Image Alt Text Generation

This plugin uses Large Language Models (LLMs) to automatically generate alternative text (alt text) for images to improve accessibility for people with disabilities. Manually entering alt text for dozens or hundreds of images in an EPUB is time-consuming and often subjective. By utilizing LLMs, you can quickly generate alt text that is easy for visually impaired users to understand.

---

### **Key Features**

- **Cost-Efficient:** Utilizes open-source LLMs through Ollama, meaning there are no LLM usage fees.
- **Version Specificity:** EPUB2 support adds image alt text, while EPUB3 support includes alt text, Roles, and accessibility meta information.
- **Customizable Prompts:** You can freely add or modify prompts to generate alt text in your preferred style. (The default prompt is configured to distinguish between covers, chapter title pages, tables, diagrams, photos, and drawings).
- **Smart Exclusions:** Set exclusion rules based on filename, Role, or image size. This allows you to skip small bullets, decorative images, or images with `role=presentation` that do not require alt text.
    
### **Requirements**

- **Ollama:** [https://ollama.com/download](https://ollama.com/download)
- **Recommended Model:** Gemma4 — `ollama pull gemma4:31b-cloud`
    
---

### **How to Use**

1. **Install the Plugin:** You can choose between English (**en**) and Korean (**ko**).
2. **Install Ollama:** Download and install from [https://ollama.com/download](https://ollama.com/download).
3. **Download the Model:** I recommend the `gemma4:31b-cloud` model. The cloud version is fast and provides enough tokens to process over 100 images.
    > **Note:** To use the cloud model, you must create an Ollama account. After installing Ollama, enter `ollama pull gemma4:31b-cloud` in your terminal. If you prefer not to sign up, use a vision-capable model that can run locally on your PC.
4. **API Configuration:** In the plugin **Settings**, go to **[API Settings]** and click **[Load]**. This will pull the list of available models if Ollama is running and connected.
5. **Connection Test:** Click **[Test API Conn]** to verify communication with the LLM.
6. **Prompt & Exclusion Management:** Modify your prompts in **[Prompt Mgmt]** and specify images to skip in **[Exclusion]**.
7. **Accessibility:** Use the **[Accessibility]** tab to add meta information to the EPUB3 OPF file.
    
---

### **Generating Alt Text**

1. **Selection:** Choose your desired **Prompt** and **Model** from the initial plugin screen.
2. **Generate:** Click the **[Generate Alt]** button in the top left to start the process.
3. **Review:** Select individual images to check the generated alt text.
4. **Roles (EPUB3):** Change the Role if necessary (default is `img`). EPUB2 users can skip this step.
5. **Regenerate:** If you want to redo a specific image, click **[Regenerate]** in the top right.
    > **Design Note:** I purposely placed **[Regenerate]** away from **[Generate Alt]** to prevent accidental clicks—I found myself making that mistake quite often when they were together!
6. **Apply:** Once everything is reviewed, click **[Apply to EPUB]**. The plugin will close, and the alt values will be saved to your file.
