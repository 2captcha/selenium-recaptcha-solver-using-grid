window.getCaptchaData = function () {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const desc = document.querySelector('.rc-imageselect-desc-wrapper');
    const comment = desc ? desc.innerText.replace(/\n/g, ' ') : '';

    const img4x4 = document.querySelector('img.rc-image-tile-44');

    // 3x3 captcha: base full image + overlays for updated tiles
    if (!img4x4) {
        const table3x3 = document.querySelector('table.rc-imageselect-table-33 > tbody');
        if (!table3x3) {
            throw new Error('Can not find reCAPTCHA 3x3 elements');
        }

        const initial3x3img = table3x3.querySelector('img.rc-image-tile-33');
        if (!initial3x3img) {
            throw new Error('Can not find base 3x3 image');
        }

        canvas.width = initial3x3img.naturalWidth;
        canvas.height = initial3x3img.naturalHeight;

        // Base image from captcha (first iteration)
        ctx.drawImage(initial3x3img, 0, 0);

        // Overlay all updated tiles (subsequent iterations)
        const updatedTiles = document.querySelectorAll('img.rc-image-tile-11');
        if (updatedTiles.length > 0) {
            const cellWidth = canvas.width / 3;
            const cellHeight = canvas.height / 3;
            const pos = [
                { x: 0, y: 0 }, { x: cellWidth, y: 0 }, { x: cellWidth * 2, y: 0 },
                { x: 0, y: cellHeight }, { x: cellWidth, y: cellHeight }, { x: cellWidth * 2, y: cellHeight },
                { x: 0, y: cellHeight * 2 }, { x: cellWidth, y: cellHeight * 2 }, { x: cellWidth * 2, y: cellHeight * 2 }
            ];

            updatedTiles.forEach((img) => {
                const td = img.closest('td');
                if (!td) {
                    return;
                }
                const index = parseInt(td.id, 10);
                if (Number.isNaN(index) || index < 0 || index > 8) {
                    return;
                }
                const p = pos[index];
                ctx.drawImage(img, p.x, p.y, cellWidth, cellHeight);
            });
        }

        return {
            rows: 3,
            columns: 3,
            type: 'GridTask',
            comment,
            body: canvas.toDataURL('image/jpeg', 0.9).replace(/^data:image\/jpeg;base64,/, '')
        };
    }

    // 4x4 captcha (single image)
    canvas.width = img4x4.naturalWidth;
    canvas.height = img4x4.naturalHeight;
    ctx.drawImage(img4x4, 0, 0);

    return {
        rows: 4,
        columns: 4,
        type: 'GridTask',
        comment,
        body: canvas.toDataURL('image/jpeg', 0.9).replace(/^data:image\/jpeg;base64,/, '')
    };
};
