#!/bin/bash

CONTAINER=$1

if [ -z "$CONTAINER" ]; then
    echo "Usage: $0 <container>"
    exit 1
fi

JS_FILES=(
    "/opt/splunk/share/splunk/search_mrsparkle/exposed/build/pages/light/search.js"
    "/opt/splunk/share/splunk/search_mrsparkle/exposed/build/pages/dark/search.js"
)

CSS_FILES=(
    "/opt/splunk/share/splunk/search_mrsparkle/exposed/build/css/bootstrap-light.css"
    "/opt/splunk/share/splunk/search_mrsparkle/exposed/build/css/bootstrap-dark.css"
)

# Créer le patch JS
PATCH_JS=$(mktemp /tmp/patch_XXXXXX.js)
cat > "$PATCH_JS" << 'EOF'

let autoExpandPropertyName = 'jsonAutoExpand';
let autoExpandSetting = localStorage.getItem(autoExpandPropertyName);
let observer2Added = false;

$(document).ready(function() {
    if (autoExpandSetting === null) {
        localStorage.setItem(autoExpandPropertyName, '0');
        autoExpandSetting = '0';
    }

    const userClickedElements = new Set();

    document.addEventListener('click', function(event) {
        if (event.target.matches('a.jscollapse')) {
            userClickedElements.add(event.target);
        }
    });

    function autoExpand() {
        let elementClicked = false;
        for (let i = 0; i <= 5; i++) {
            document.querySelectorAll('a.jsexpands').forEach(function(expander) {
                if (!userClickedElements.has(expander)) {
                    expander.click();
                    elementClicked = true;
                }
            });
        }
        if (elementClicked) {
            $(".events-controls-inner").click();
        }
    }

    function toggleExpand() {
        let elementClicked = false;
        userClickedElements.clear();
        $(".jscollapse").each(function() {
            const parentNode = $(this).parent()[0];
            if (parentNode.className === 'json-tree shared-jsontree') {
                return;
            }
            if ($(this).html() === '[-]') {
                $(this)[0].click();
                elementClicked = true;
            }
        });
        if (elementClicked) {
            $(".events-controls-inner").click();
        }
    }

    function setupSwitch() {
        const switchElement = $(".switch")[0];
        if (switchElement) {
            switchElement.childNodes[0].checked = (localStorage.getItem(autoExpandPropertyName) === '1');
            if (localStorage.getItem(autoExpandPropertyName) === '1'){
                autoExpand()
            }
        } else {
            setTimeout(setupSwitch, 500);
        }
    }

    function setupSlider() {
        const slider = document.querySelector('.slider');
        if (slider) {
            if (!slider.hasEventListener) {
                slider.addEventListener('click', () => {
                    const switchElement = $(".switch")[0].childNodes[0];
                    if (switchElement && switchElement.checked === false) {
                        localStorage.setItem(autoExpandPropertyName, '1');
                        $(".switch")[0].childNodes[0] = true;
                        autoExpand();
                    } else if (switchElement) {
                        localStorage.setItem(autoExpandPropertyName, '0');
                        $(".switch")[0].childNodes[0] = false;
                        toggleExpand();
                    }
                });
                slider.hasEventListener = true;
            }
        }
    }

    // Changé : Map uid -> { added_by, description } au lieu d'un Set
    let lookupUids = new Map();
    let lookupLoaded = true;
    let UID_FIELD = 'uid';

    function getUidFromRow($row) {
        let foundUid = null;

        // Méthode 1 : cherche via data-field-name
        $row.find('a.f-v[data-field-name="' + UID_FIELD + '"]').each(function() {
            foundUid = $(this).text().trim();
        });

        // Méthode 2 : fallback — cherche dans le JSON brut (span[data-path])
        if (!foundUid) {
            $row.find('span[data-path="' + UID_FIELD + '"]').each(function() {
                foundUid = $(this).text().trim();
            });
        }

        // Méthode 3 : fallback — cherche dans le bloc selectedfields visible
        if (!foundUid) {
            $row.find('.shared-eventsviewer-list-body-row-selectedfields li').each(function() {
                const $li = $(this);
                const label = $li.find('span.field').text().trim().replace(/\s*=\s*$/, '');
                if (label === UID_FIELD) {
                    foundUid = $li.find('a.f-v').attr('title') || $li.find('a.f-v').text().trim();
                }
            });
        }

        return foundUid;
    }

    function badgeMatchingRows() {
        if (!lookupLoaded) return;

        $('.shared-eventsviewer-list-body-row').each(function() {
            const $row = $(this);

            if ($row.find('.lookup-badge').length > 0) return;

            const uid = getUidFromRow($row);
            const meta = uid && lookupUids.get(uid);

            const $targetCell = $row.find('td.event').first();

            if (meta) {
                const addedBy   = meta.added_by    || 'Unknown';
                const desc      = meta.description || 'No description';
                $targetCell.prepend(
                    '<span class="lookup-badge lookup-badge-in">🚩 Flagged by ' + addedBy + ' | ' + desc + ' 🚩</span>'
                );
                $row.addClass('lookup-match-row');
            }
        });
    }

    function setupLookupObserver() {
        const target = document.querySelector(
            '.shared-eventsviewer-list tbody, ' +
            '.shared-eventsviewer tbody'
        );

        if (!target) {
            setTimeout(setupLookupObserver, 1000);
            return;
        }

        const observer = new MutationObserver(function() {
            badgeMatchingRows();
        });

        observer.observe(target, { childList: true, subtree: true });
        console.log('[LookupBadge] Observer actif v2');
    }

    function fetchLookupUids(lookupName, uidField, callback) {
        require(['splunkjs/mvc'], function(mvc) {
            var service = mvc.createService();

            service.post(
                '/services/search/jobs',
                {
                    // Changé : on récupère aussi added_by et description
                    search: '| inputlookup flagged_events | fields id, added_by, description | dedup id',
                    output_mode: 'json',
                    exec_mode: 'oneshot',
                    count: 10000
                },
                function(err, response) {
                    if (err) {
                        console.error('[LookupBadge] ❌ Erreur:', err);
                        return;
                    }

                    const results = response.data.results || [];
                    results.forEach(function(row) {
                        if (row['id']) {
                            // Changé : on stocke un objet dans la Map
                            lookupUids.set(row['id'].trim(), {
                                added_by:    (row['added_by']    || '').trim(),
                                description: (row['description'] || '').trim()
                            });
                        }
                    });

                    lookupLoaded = true;
                    console.log('[LookupBadge] ✅ ' + lookupUids.size + ' UIDs chargés');
                }
            );
        });
    }

    fetchLookupUids('flagged_events', 'id', function(err, uids) {
        if (err) return;
        console.log('[LookupTest] Map prête, taille:', uids.size);
    });

    // Init
    setupLookupObserver();
    badgeMatchingRows();

    setupSlider();
    setupSwitch();
    setInterval(setupSlider, 500);
    setInterval(setupSwitch, 500);
});
EOF

# Créer le patch CSS
PATCH_CSS=$(mktemp /tmp/patch_XXXXXX.css)
cat > "$PATCH_CSS" << 'EOF'

/* The switch - the box around the slider*/
.autoexpand {
    margin-top: 2px;
}
.autoexpandtext {
    margin-right: 5px;
}
.switch {
    position: relative;
    display: inline-block;
    width: 43px;
    height: 18px;
    margin-top: 5px;
    margin-bottom: 0px;
}
/* Hide default HTML checkbox */
.switch input {
    opacity: 0;
    width: 0;
    height: 0;
}
/* The slider */
.slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    -webkit-transition: .4s;
    transition: .4s;
}
.slider:before {
    position: absolute;
    content: "";
    height: 10px;
    width: 10px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    -webkit-transition: .4s;
    transition: .4s;
}
input:checked + .slider {
    background-color: rgb(92, 192, 92);
}
input:focus + .slider {
    box-shadow: 0 0 1px #2196F3;
}
input:checked + .slider:before {
    -webkit-transform: translateX(26px);
    -ms-transform: translateX(26px);
    transform: translateX(26px);
}
/* Rounded sliders */
.slider.round {
    border-radius: 34px;
}
.slider.round:before {
    border-radius: 50%;
}

/* ── Lookup Badge base ── */
.lookup-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    margin-right: 8px;
    vertical-align: middle;
    white-space: nowrap;
    letter-spacing: 0.3px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    transition: opacity 0.2s;
}

.lookup-badge:hover {
    opacity: 0.85;
}

/* ── In Lookup — vert ── */
.lookup-badge-in {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    color: #fff;
    border: 1px solid rgba(39, 174, 96, 0.4);
}

/* ── Not in Lookup — gris bleuté ── */
.lookup-badge-out {
    background: linear-gradient(135deg, #7f8c8d, #636e72);
    color: #fff;
    border: 1px solid rgba(99, 110, 114, 0.4);
}

/* ── Row highlight ── */
.lookup-match-row > td {
    background-color: rgba(46, 204, 113, 0.06) !important;
}

EOF

# Copier les patches dans le container
docker cp "$PATCH_JS"  "$CONTAINER:/tmp/patch.js"
docker cp "$PATCH_CSS" "$CONTAINER:/tmp/patch.css"

# Patch JS
for FILE in "${JS_FILES[@]}"; do
    echo "⏳ Traitement JS : $FILE..."

    docker exec -u root "$CONTAINER" test -f "$FILE"
    if [ $? -ne 0 ]; then
        echo "❌ Fichier introuvable : $FILE"
        continue
    fi

    docker exec -u root "$CONTAINER" sed -i 's|<div class="pull-right jobstatus-control-grouping"></div>|<div class="pull-right jobstatus-control-grouping"><div class="autoexpand"><span class="autoexpandtext">Expand JSON</span><label class="switch"><input type="checkbox" checked><span class="slider round"></span></label></div></div>|g' "$FILE"

    docker exec -u root "$CONTAINER" bash -c "cat /tmp/patch.js >> '$FILE'"

    echo "✅ $FILE patché"
done

# Patch CSS
for FILE in "${CSS_FILES[@]}"; do
    echo "⏳ Traitement CSS : $FILE..."

    docker exec -u root "$CONTAINER" test -f "$FILE"
    if [ $? -ne 0 ]; then
        echo "❌ Fichier introuvable : $FILE"
        continue
    fi

    docker exec -u root "$CONTAINER" bash -c "cat /tmp/patch.css >> '$FILE'"

    echo "✅ $FILE patché"
done

# Nettoyage
docker exec -u root "$CONTAINER" rm /tmp/patch.js /tmp/patch.css
rm "$PATCH_JS" "$PATCH_CSS"

echo ""
echo "🎉 Patch terminé sur le container '$CONTAINER'"