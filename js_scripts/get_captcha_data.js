window.getCaptchaData = () => {
    return new Promise((resolve, reject) => {
        let canvas = document.createElement('canvas');
        let ctx = canvas.getContext('2d');
        let comment = document.querySelector('.rc-imageselect-desc-wrapper').innerText.replace(/\n/g, ' ');

        let img4x4 = document.querySelector('img.rc-image-tile-44');
        if (!img4x4) {
            let table3x3 = document.querySelector('table.rc-imageselect-table-33 > tbody');
            if (!table3x3) {
                reject('Can not find reCAPTCHA elements');
            }

            let initial3x3img = table3x3.querySelector('img.rc-image-tile-33');

            canvas.width = initial3x3img.naturalWidth;
            canvas.height = initial3x3img.naturalHeight;
            ctx.drawImage(initial3x3img, 0, 0);

            let updatedTiles = document.querySelectorAll('img.rc-image-tile-11');

            if (updatedTiles.length > 0) {
                const pos = [
                    { x: 0, y: 0 }, { x: ctx.canvas.width / 3, y: 0 }, { x: ctx.canvas.width / 3 * 2, y: 0 },
                    { x: 0, y: ctx.canvas.height / 3 }, { x: ctx.canvas.width / 3, y: ctx.canvas.height / 3 }, { x: ctx.canvas.width / 3 * 2, y: ctx.canvas.height / 3 },
                    { x: 0, y: ctx.canvas.height / 3 * 2 }, { x: ctx.canvas.width / 3, y: ctx.canvas.height / 3 * 2 }, { x: ctx.canvas.width / 3 * 2, y: ctx.canvas.height / 3 * 2 }
                ];
                updatedTiles.forEach((t) => {
                    const ind = t.parentElement.parentElement.parentElement.tabIndex - 3;
                    ctx.drawImage(t, pos[ind - 1].x, pos[ind - 1].y);
                });
            }
            resolve({
                rows: 3,
                columns: 3,
                type: 'GridTask',
                comment,
                body: canvas.toDataURL().replace(/^data:image\/?[A-z]*;base64,/, '')
            });
        } else {
            canvas.width = img4x4.naturalWidth;
            canvas.height = img4x4.naturalHeight;
            ctx.drawImage(img4x4, 0, 0);
            resolve({
                rows: 4,
                columns: 4,
                comment,
                body: canvas.toDataURL('image/jpeg', 0.8).replace(/^data:image\/jpeg;base64,/, ''),
                type: 'GridTask'
            });
        }
    });
};