/*This is the javascript for the popup*/


document.addEventListener('DOMContentLoaded', () => {
    const treeCount = document.getElementById('tree-count');
    const forest = document.getElementById('forest');
    const altProducts = document.getElementById('alt-products');
    const alternativesSection = document.getElementById('alternatives');

    // Get data from Chrome's local storage
    chrome.storage.local.get(['ecoData'], (result) => {
        if (result.ecoData && result.ecoData.score !== undefined) {
            const { score, alternatives } = result.ecoData;

            treeCount.textContent = `You saved a total of ${score} trees!`;

            const numberOfTrees = Math.round(score / 10);
            forest.innerHTML = '';
            for (let i = 0; i < numberOfTrees; i++) {
                const tree = document.createElement('div');
                tree.className = 'tree';
                tree.style.animationDelay = `${i * 0.1}s`;
                forest.appendChild(tree);
            }

            if (alternatives && alternatives.length > 0) {
                 alternativesSection.style.display = 'block';
                 altProducts.innerHTML = '';
                alternatives.forEach(alt => {
                    const listItem = document.createElement('li');
                    const link = document.createElement('a');
                    link.href = `https://www.amazon.com/dp/${alt.asin}`;
                    link.target = '_blank';
                    link.textContent = `${alt.title} - Score: ${alt.score}`;
                    listItem.appendChild(link);
                    altProducts.appendChild(listItem);
                });
            } else {
                 alternativesSection.style.display = 'none';
            }

        } else {
            treeCount.textContent = 'Ready to save the Amazon!';
            alternativesSection.style.display = 'none';
            forest.innerHTML = '<p style="font-size: 14px; color: #555; padding: 0 10px;">Navigate to an Amazon product page to see how many trees you saved. (if trees do not show, refresh the amazon page and rerun the extension)</p>';
        }
    });
});