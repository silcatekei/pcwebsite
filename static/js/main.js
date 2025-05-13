// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const draggables = document.querySelectorAll('.draggable-part');
    const dropTargets = document.querySelectorAll('.component-slot');
    const selectedPartsList = document.getElementById('selected-parts-list');
    const checkCompatibilityBtn = document.getElementById('check-compatibility-btn');
    const compatibilityResultsDiv = document.getElementById('compatibility-results');
    const clearBuildBtn = document.getElementById('clear-build-btn');
    const partSearchInput = document.getElementById('part-search-input');
    const allDraggableParts = document.querySelectorAll('#parts-palette .draggable-part'); // Used for search and display updates

    let currentBuild = {};
    let activeDraggedElement = null; // Keep track of the actual DOM element being dragged
    let activeDraggedItemData = null; // Data for the item being dragged

    draggables.forEach(part => {
        part.addEventListener('dragstart', (e) => {
            activeDraggedElement = part; // Store the DOM element
            activeDraggedItemData = {
                id: part.dataset.partId,
                type: part.dataset.partType,
                name: part.querySelector('span').textContent,
                img: part.dataset.partImg,
                searchableName: part.dataset.partName
            };

            e.dataTransfer.setData('text/plain', activeDraggedItemData.id);
            e.dataTransfer.setData('part-type', activeDraggedItemData.type); // For quick check in dragover

            // Set opacity slightly after the drag image is created by the browser
            setTimeout(() => {
                if (activeDraggedElement) { // Check if it's still the active drag
                    activeDraggedElement.style.opacity = '0.5';
                }
            }, 0);
        });

        part.addEventListener('dragend', (e) => {
            // Always restore opacity of the element that started the drag
            // regardless of whether the drop was successful or not.
            if (activeDraggedElement) {
                activeDraggedElement.style.opacity = '1';
            }
            // Clear these regardless of drop success, as the drag operation has ended.
            activeDraggedElement = null;
            activeDraggedItemData = null;
        });
    });

    dropTargets.forEach(slot => {
        slot.addEventListener('dragover', (e) => {
            e.preventDefault();
            // Use activeDraggedItemData for type checking if available, otherwise fallback to dataTransfer
            const typeToCheck = activeDraggedItemData ? activeDraggedItemData.type : e.dataTransfer.getData('part-type');
            if (slot.dataset.dropTargetType === typeToCheck) {
                slot.classList.add('drag-over');
            }
        });

        slot.addEventListener('dragleave', () => {
            slot.classList.remove('drag-over');
        });

        slot.addEventListener('drop', (e) => {
            e.preventDefault();
            slot.classList.remove('drag-over');

            // Crucially, use the data stored at dragstart (activeDraggedItemData)
            if (!activeDraggedItemData || slot.dataset.dropTargetType !== activeDraggedItemData.type) {
                console.warn("Drop failed: Mismatched type or no active dragged item data.");
                return;
            }

            const { id: partId, type: partType, name: partName, img: partImgSrc } = activeDraggedItemData;

            slot.innerHTML = '';
            const img = document.createElement('img');
            img.src = partImgSrc;
            img.alt = partName;
            img.classList.add('dropped-part-img');

            const nameSpan = document.createElement('span');
            nameSpan.textContent = partName;
            nameSpan.style.fontSize = "0.8em";
            nameSpan.style.marginTop = "5px";

            slot.appendChild(img);
            slot.appendChild(nameSpan);

            currentBuild[partType] = partId;
            updateSelectedPartsDisplay();
            console.log(`Dropped ${partName} (${partId}) into ${partType} slot.`);
        });
    });

    function updateSelectedPartsDisplay() {
        selectedPartsList.innerHTML = '';
        Object.keys(currentBuild).forEach(partType => {
            const partId = currentBuild[partType];
            if (partId) {
                let displayName = `Part ID: ${partId}`;
                let displayImgSrc = `static/images/${partType}_placeholder.png`;

                const originalDraggable = Array.from(allDraggableParts).find(d => d.dataset.partId === partId && d.dataset.partType === partType);
                if (originalDraggable) {
                    displayName = originalDraggable.querySelector('span').textContent;
                    displayImgSrc = originalDraggable.dataset.partImg;
                }

                const li = document.createElement('li');
                const imgEl = document.createElement('img');
                imgEl.src = displayImgSrc;
                imgEl.alt = displayName;
                imgEl.style.width = '30px';
                imgEl.style.height = '30px';
                imgEl.style.objectFit = 'contain';
                imgEl.style.marginRight = '8px';

                li.appendChild(imgEl);
                li.appendChild(document.createTextNode(`${partType.toUpperCase()}: ${displayName}`));
                selectedPartsList.appendChild(li);
            }
        });
        if (selectedPartsList.children.length === 0) {
            selectedPartsList.innerHTML = '<li>No parts selected.</li>';
        }
    }
    updateSelectedPartsDisplay();

    function resetSlot(slotElement) {
        const slotType = slotElement.dataset.dropTargetType;
        const placeholderSrc = slotElement.dataset.placeholderImgSrc; // FIXED: Removed trailing slash

        slotElement.innerHTML = '';
        const label = document.createElement('span');
        label.classList.add('slot-label');
        label.textContent = slotType.charAt(0).toUpperCase() + slotType.slice(1);
        slotElement.appendChild(label);

        // If you want to add back placeholder images on reset:
        if (placeholderSrc) {
            const placeholderImg = document.createElement('img');
            placeholderImg.src = placeholderSrc;
            placeholderImg.classList.add('slot-placeholder-img');
            placeholderImg.alt = `${slotType.charAt(0).toUpperCase() + slotType.slice(1)} Slot`;
            slotElement.appendChild(placeholderImg);
        }
    }

    if (clearBuildBtn) {
        clearBuildBtn.addEventListener('click', () => {
            currentBuild = {};
            dropTargets.forEach(slot => {
                resetSlot(slot);
            });
            updateSelectedPartsDisplay();
            if (compatibilityResultsDiv) {
                compatibilityResultsDiv.innerHTML = '';
                compatibilityResultsDiv.className = '';
            }
            console.log("Build cleared!");
        });
    }

    if (checkCompatibilityBtn) {
        checkCompatibilityBtn.addEventListener('click', async () => {
            if (Object.keys(currentBuild).length === 0) {
                compatibilityResultsDiv.textContent = "Add some parts to your build first!";
                compatibilityResultsDiv.className = '';
                return;
            }
            compatibilityResultsDiv.textContent = "Checking compatibility...";
            compatibilityResultsDiv.className = '';
            try {
                const response = await fetch('/api/check_compatibility', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentBuild),
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status} ${await response.text()}`);
                }
                const result = await response.json();
                compatibilityResultsDiv.innerHTML = '';
                result.messages.forEach(msg => {
                    const p = document.createElement('p');
                    p.textContent = msg;
                    compatibilityResultsDiv.appendChild(p);
                });
                if (result.compatible) {
                    compatibilityResultsDiv.classList.add('compatible');
                } else {
                    compatibilityResultsDiv.classList.add('incompatible');
                }
            } catch (error) {
                compatibilityResultsDiv.textContent = `Error: ${error.message}`;
                compatibilityResultsDiv.classList.add('incompatible');
                console.error("Compatibility check error:", error);
            }
        });
    }

    if (partSearchInput && allDraggableParts.length > 0) {
        partSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            allDraggableParts.forEach(partElement => {
                const partSearchableName = partElement.dataset.partName;
                if (partSearchableName.includes(searchTerm)) {
                    partElement.style.display = 'flex';
                } else {
                    partElement.style.display = 'none';
                }
            });

            const categories = document.querySelectorAll('#parts-palette .part-category');
            categories.forEach(category => {
                let hasVisiblePart = false;
                const partsInCategory = category.querySelectorAll('.draggable-part');
                partsInCategory.forEach(part => {
                    if (part.style.display !== 'none') {
                        hasVisiblePart = true;
                    }
                });
                if (searchTerm === "" || hasVisiblePart) {
                    category.style.display = 'block';
                } else {
                    category.style.display = 'none';
                }
            });
        });
    }
});