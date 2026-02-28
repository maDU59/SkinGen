async function convertTexture(url) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = url;

        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 64;
            canvas.height = 64;

            ctx.drawImage(img, 0, 0);

            function drawFlipped(sx, sy, dx, dy, w, h) {
                ctx.save();
                ctx.translate(dx + w, dy);
                ctx.scale(-1, 1);
                ctx.drawImage(img, sx, sy, w, h, 0, 0, w, h);
                ctx.restore();
            }

            drawFlipped(0, 20, 24, 52, 4, 12);
            drawFlipped(4, 20, 20, 52, 4, 12);
            drawFlipped(8, 20, 16, 52, 4, 12);
            drawFlipped(12, 20, 28, 52, 4, 12);
            drawFlipped(4, 16, 20, 48, 4, 4);
            drawFlipped(8, 16, 24, 48, 4, 4);

            drawFlipped(40, 20, 40, 52, 4, 12);
            drawFlipped(44, 20, 36, 52, 4, 12);
            drawFlipped(48, 20, 32, 52, 4, 12);
            drawFlipped(52, 20, 44, 52, 4, 12);
            drawFlipped(44, 16, 36, 48, 4, 4);
            drawFlipped(48, 16, 40, 48, 4, 4);
            const resultImg = new Image();
            resultImg.onload = () => resolve(resultImg);
            resultImg.src = canvas.toDataURL("image/png");
        };

        img.onerror = () => reject("Failed to load skin.");
    });
}