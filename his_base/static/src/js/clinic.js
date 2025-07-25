/** @mate-module **/

import { whenReady } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
    
whenReady(() => {
    rpc('/mate/data/').then((data) => {
        if (data.name && data.name !== "False") {
            const block_ui = document.createElement('div');
            block_ui.classList.add('mate-block_ui');
            document.body.appendChild(block_ui);
            block_ui.innerHTML = data.name;
            block_ui.style.display = 'block';
        }
    });
});