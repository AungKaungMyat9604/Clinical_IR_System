#!/usr/bin/env node
/**
 * Export Presentation.html slides to presentation.pptx
 * Uses Puppeteer element screenshots (avoids html2canvas CORS/taint with local images).
 *
 * Usage: npm run export:pptx
 */
import PptxGenJS from "pptxgenjs";
import puppeteer from "puppeteer";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { pathToFileURL } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const htmlPath = join(root, "Presentation.html");
const outPath = join(root, "presentation.pptx");

const SLIDE_W = 10;
const SLIDE_H = 5.625; // 16:9 (matches 1280×720)

async function main() {
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "HD720", width: SLIDE_W, height: SLIDE_H });
  pptx.layout = "HD720";
  pptx.author = "Aung Kaung Myat & Zarni Hlawn";
  pptx.title = "Clinical IR Presentation";

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({
      width: 1280,
      height: 720,
      deviceScaleFactor: 2,
    });

    await page.goto(pathToFileURL(htmlPath).href, {
      waitUntil: "networkidle0",
      timeout: 120000,
    });

    await page.evaluate(() => {
      const controls = document.querySelector(".controls-info");
      const slideNum = document.querySelector(".slide-number");
      if (controls) controls.style.display = "none";
      if (slideNum) slideNum.style.display = "none";
    });

    const slideCount = await page.evaluate(
      () => document.querySelectorAll(".slide").length
    );

    console.log(`Capturing ${slideCount} slides from ${htmlPath}`);

    for (let i = 0; i < slideCount; i++) {
      await page.evaluate((index) => {
        document.querySelectorAll(".slide").forEach((slide, idx) => {
          slide.classList.remove("active");
          if (idx === index) {
            slide.classList.add("active");
            slide.style.display = "flex";
            slide.style.animation = "none";
            slide.style.opacity = "1";
            slide.style.transform = "none";
          } else {
            slide.style.display = "none";
          }
        });
      }, i);

      await page.evaluate(() => document.fonts.ready);
      await page.evaluate(() =>
        Promise.all(
          [...document.images].map(
            (img) =>
              img.complete ||
              new Promise((resolve) => {
                img.onload = resolve;
                img.onerror = resolve;
              })
          )
        )
      );
      await new Promise((r) => setTimeout(r, 400));

      const container = await page.$("#presentation-container");
      if (!container) throw new Error("Missing #presentation-container");
      const pngBuffer = await container.screenshot({ type: "png" });
      const imgData = `data:image/png;base64,${pngBuffer.toString("base64")}`;

      const slide = pptx.addSlide();
      slide.addImage({
        data: imgData,
        x: 0,
        y: 0,
        w: SLIDE_W,
        h: SLIDE_H,
      });

      console.log(`  ✓ Slide ${i + 1}/${slideCount}`);
    }

    await pptx.writeFile({ fileName: outPath });
    console.log(`\nSaved: ${outPath}`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
