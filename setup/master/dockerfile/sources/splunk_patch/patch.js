// PATCHED v1.0.0
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

    // Changed: Map uid -> { added_by, description } instead of a Set
    let lookupUids = new Map();
    let lookupLoaded = true;
    let UID_FIELD = 'uid';

    var MITRE_OPTS = [
        'Reconnaissance','Resource Development','Initial Access','Execution',
        'Persistence','Privilege Escalation','Defense Evasion','Credential Access',
        'Discovery','Lateral Movement','Collection','Command and Control',
        'Exfiltration','Impact','FIXME'
    ];
    var STATUS_OPTS = ['Suspicious','Under Investigation','Malicious','Benign','False Positive','FIXME'];

    var L_STYLE   = 'display:block;font-size:11px;font-weight:700;text-transform:uppercase;' +
                    'letter-spacing:.05em;color:#5c656e;margin-bottom:4px;margin-top:12px;';
    var IN_STYLE  = 'width:100%;padding:6px 8px;border:1px solid #c3cbd4;border-radius:3px;' +
                    'font-size:13px;box-sizing:border-box;font-family:inherit;color:#1a1c1e;';
    var SEL_STYLE = IN_STYLE + 'background:#fff;cursor:pointer;';

    var mitreOptions  = '<option value="">-- Select --</option>' +
        MITRE_OPTS.map(function(t) { return '<option value="' + t + '">' + t + '</option>'; }).join('');
    var statusOptions = '<option value="">-- Select --</option>' +
        STATUS_OPTS.map(function(s) { return '<option value="' + s + '">' + s + '</option>'; }).join('');

    // ── Flag event modal ──
    $('body').append(
        '<div id="flag-event-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;' +
        'background:rgba(0,0,0,0.4);z-index:10000;justify-content:center;align-items:center;">' +
          '<div style="background:#fff;border-radius:4px;padding:24px;width:460px;max-width:95%;' +
          'box-shadow:0 8px 32px rgba(0,0,0,.2);border:1px solid #c3cbd4;">' +
            '<h3 style="margin-top:0;font-size:15px;color:#1a1c1e;border-bottom:1px solid #eaedf0;' +
            'padding-bottom:12px;margin-bottom:4px;">🚩 Flag Event</h3>' +
            '<label style="' + L_STYLE + '">Added by</label>' +
            '<input id="flag-modal-added-by" type="text" style="' + IN_STYLE + '" />' +
            '<label style="' + L_STYLE + '">Description</label>' +
            '<input id="flag-modal-desc" type="text" placeholder="e.g. Suspicious PowerShell execution" style="' + IN_STYLE + '" />' +
            '<label style="' + L_STYLE + '">MITRE Tactic</label>' +
            '<select id="flag-modal-mitre" style="' + SEL_STYLE + '">' + mitreOptions + '</select>' +
            '<label style="' + L_STYLE + '">Status</label>' +
            '<select id="flag-modal-status-sel" style="' + SEL_STYLE + ';margin-bottom:16px;">' + statusOptions + '</select>' +
            '<div style="display:flex;justify-content:flex-end;gap:8px;">' +
              '<button id="flag-modal-cancel" style="padding:6px 14px;border:1px solid #c3cbd4;border-radius:3px;' +
              'background:#fff;cursor:pointer;font-size:13px;color:#1a1c1e;">Cancel</button>' +
              '<button id="flag-modal-confirm" style="padding:6px 14px;border:none;border-radius:3px;' +
              'background:#e74c3c;color:#fff;cursor:pointer;font-size:13px;font-weight:600;">🚩 Flag</button>' +
            '</div>' +
            '<div id="flag-modal-status" style="margin-top:10px;font-size:12px;min-height:18px;"></div>' +
          '</div>' +
        '</div>'
    );

    var pendingFlagUid = null;
    var pendingFlagRow = null;

    function unflagEvent(uid, $row) {
        if (!confirm('Remove flag from this event?')) return;

        function escSpl(s) {
            return String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
        }

        require(['splunkjs/mvc'], function(mvc) {
            var service = mvc.createService();
            var unflagSpl = '| inputlookup flagged_events'
                + ' | eval flag = if(id="' + escSpl(uid) + '", 0, flag)'
                + ' | where flag=1'
                + ' | outputlookup flagged_events';

            service.post('/services/search/jobs', {
                search:      unflagSpl,
                output_mode: 'json',
                exec_mode:   'oneshot',
                count:       0
            }, function(err) {
                if (err) {
                    alert('Error removing flag: ' + err);
                    return;
                }

                lookupUids.delete(uid);

                if ($row) {
                    $row.find('.flag-badge-wrap').remove();
                    $row.removeClass('lookup-match-row');

                    var $flagBtn = $('<button class="flag-btn" title="Flag">🚩 Flag</button>');
                    $flagBtn.on('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        showFlagModal(uid, $row);
                    });
                    $row.find('a.toggle-raw-json').first().after($flagBtn);
                }
            });
        });
    }

    function showFlagModal(uid, $row) {
        pendingFlagUid = uid;
        pendingFlagRow = $row;
        var currentUser = (typeof Splunk !== 'undefined' && Splunk.util)
            ? Splunk.util.getConfigValue('USERNAME') : '';
        $('#flag-modal-added-by').val(currentUser);
        $('#flag-modal-desc').val('');
        $('#flag-modal-mitre').val('FIXME');
        $('#flag-modal-status-sel').val('FIXME');
        $('#flag-modal-status').text('').css('color', '');
        $('#flag-modal-confirm').prop('disabled', false).text('🚩 Flag');
        $('#flag-event-modal').css('display', 'flex');
        setTimeout(function() { $('#flag-modal-desc').focus(); }, 100);
    }

    $('#flag-modal-cancel').on('click', function() {
        $('#flag-event-modal').hide();
        pendingFlagUid = null;
        pendingFlagRow = null;
    });

    $('#flag-event-modal').on('click', function(e) {
        if (e.target === this) {
            $(this).hide();
            pendingFlagUid = null;
            pendingFlagRow = null;
        }
    });

    $('#flag-modal-desc').on('keydown', function(e) {
        if (e.key === 'Enter')  { $('#flag-modal-confirm').trigger('click'); }
        if (e.key === 'Escape') { $('#flag-modal-cancel').trigger('click'); }
    });

    $('#flag-modal-confirm').on('click', function() {
        if (!pendingFlagUid) return;
        var uid    = pendingFlagUid;
        var $row   = pendingFlagRow;
        var addedBy = $('#flag-modal-added-by').val().trim() || 'unknown';
        var desc    = $('#flag-modal-desc').val().trim();
        var mitre   = $('#flag-modal-mitre').val()      || 'FIXME';
        var status  = $('#flag-modal-status-sel').val() || 'FIXME';

        function escSpl(s) {
            return String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
        }

        function setModalStatus(msg, color) {
            $('#flag-modal-status').text(msg).css('color', color || '#6c757d');
        }

        setModalStatus('Resolving event…');
        $('#flag-modal-confirm').prop('disabled', true).text('Saving…');

        require(['splunkjs/mvc'], function(mvc) {
            var service = mvc.createService();

            service.post('/services/search/jobs', {
                search: '| tstats count WHERE index=* uid="' + escSpl(uid) + '" BY index '
                      + '| stats sum(count) as found, latest(index) as resolved_idx '
                      + '| appendpipe [stats count | eval found=0, resolved_idx="" | fields found resolved_idx] '
                      + '| stats max(found) as found, max(resolved_idx) as resolved_idx',
                output_mode:   'json',
                exec_mode:     'oneshot',
                count:          1,
                earliest_time: '0',
                latest_time:   'now'
            }, function(err, response) {
                if (err) {
                    setModalStatus('Error resolving event: ' + err, '#dc3545');
                    $('#flag-modal-confirm').prop('disabled', false).text('🚩 Flag');
                    return;
                }

                var results     = (response.data && response.data.results) || [];
                var first       = results[0] || {};
                var found       = parseInt(first.found, 10) || 0;
                var resolvedIdx = first.resolved_idx || '';

                if (found === 0 || !resolvedIdx) {
                    setModalStatus('Event UID not found in any accessible index', '#dc3545');
                    $('#flag-modal-confirm').prop('disabled', false).text('🚩 Flag');
                    return;
                }

                var flagSpl = '| makeresults'
                    + ' | eval id="'           + escSpl(uid)         + '"'
                    + ' | eval flag=1'
                    + ' | eval added_by="'     + escSpl(addedBy)     + '"'
                    + ' | eval added_when=now()'
                    + ' | eval idx="'          + escSpl(resolvedIdx) + '"'
                    + ' | eval description="'  + escSpl(desc)        + '"'
                    + ' | eval mitre_tactic="' + escSpl(mitre)       + '"'
                    + ' | eval status="'       + escSpl(status)      + '"'
                    + ' | append [ | inputlookup flagged_events ]'
                    + ' | stats latest(flag) as flag latest(added_by) as added_by'
                    +         ' latest(added_when) as added_when latest(idx) as idx'
                    +         ' latest(description) as description latest(mitre_tactic) as mitre_tactic'
                    +         ' latest(status) as status by id'
                    + ' | outputlookup flagged_events';

                service.post('/services/search/jobs', {
                    search:      flagSpl,
                    output_mode: 'json',
                    exec_mode:   'oneshot',
                    count:       0
                }, function(err2) {
                    $('#flag-modal-confirm').prop('disabled', false).text('🚩 Flag');
                    if (err2) {
                        setModalStatus('Error saving flag: ' + err2, '#dc3545');
                        return;
                    }

                    lookupUids.set(uid, { added_by: addedBy, description: desc });

                    if ($row) {
                        $row.find('.flag-btn').remove();
                        var descDisplay = desc || 'No description';
                        var $wrap2 = $('<span class="flag-badge-wrap"></span>');
                        var $ub = $('<button class="unflag-btn" title="Remove flag">🏳️ Unflag</button>');
                        (function(u, r) {
                            $ub.on('click', function(e) {
                                e.stopPropagation();
                                e.preventDefault();
                                unflagEvent(u, r);
                            });
                        })(uid, $row);

                        $wrap2.append($ub);
                        $wrap2.append('<span class="separator"> | </span>');
                        $wrap2.append('<span class="lookup-badge lookup-badge-in">Flagged by ' + addedBy + ' | ' + descDisplay + '</span>');

                        $row.find('a.toggle-raw-json').first().after($wrap2);
                        $row.addClass('lookup-match-row');
                    }

                    $('#flag-event-modal').hide();
                    pendingFlagUid = null;
                    pendingFlagRow = null;
                });
            });
        });
    });

    function getUidFromRow($row) {
        let foundUid = null;

        // Method 1: look up via data-field-name attribute
        $row.find('a.f-v[data-field-name="' + UID_FIELD + '"]').each(function() {
            foundUid = $(this).text().trim();
        });

        // Method 2: fallback — search in raw JSON (span[data-path])
        if (!foundUid) {
            $row.find('span[data-path="' + UID_FIELD + '"]').each(function() {
                foundUid = $(this).text().trim();
            });
        }

        // Method 3: fallback — search in the visible selectedfields block
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

            // Skip rows already processed by this version of the patch
            if ($row.find('.flag-badge-wrap').length > 0 || $row.find('.flag-btn').length > 0) return;
            // Clean up bare badge left by a previous patch version
            $row.find('td.event > .lookup-badge').remove();
            $row.removeClass('lookup-match-row');

            const uid = getUidFromRow($row);
            const meta = uid && lookupUids.get(uid);

            const $targetCell = $row.find('a.toggle-raw-json').first();

            if (meta) {
                const addedBy = meta.added_by || 'Unknown';
                const desc = meta.description || 'No description';
                var $wrap = $('<span class="flag-badge-wrap"></span>');
                var $unflagBtn = $('<button class="unflag-btn" title="Remove flag">🏳️ Unflag</button>');
                (function(capturedUid, capturedRow) {
                    $unflagBtn.on('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        unflagEvent(capturedUid, capturedRow);
                    });
                })(uid, $row);

                $wrap.append($unflagBtn);
                $wrap.append('<span class="separator"> | </span>');
                $wrap.append('<span class="lookup-badge lookup-badge-in">Flagged by ' + addedBy + ' | ' + desc + '</span>');

                $targetCell.after($wrap);
                $row.addClass('lookup-match-row');
            } else if (uid) {
                var $flagBtn = $('<button class="flag-btn" title="Flag">🚩 Flag</button>');
                $flagBtn.on('click', function(e) {
                    e.stopPropagation();
                    e.preventDefault();
                    showFlagModal(uid, $row);
                });
                $targetCell.after($flagBtn);
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
        console.log('[LookupBadge] Observer active v2');
    }

    function fetchLookupUids(lookupName, uidField, callback) {
        require(['splunkjs/mvc'], function(mvc) {
            var service = mvc.createService();

            service.post(
                '/services/search/jobs',
                {
                    // Changed: also fetch added_by and description
                    search: '| inputlookup flagged_events | fields id, added_by, description | dedup id',
                    output_mode: 'json',
                    exec_mode: 'oneshot',
                    count: 10000
                },
                function(err, response) {
                    if (err) {
                        console.error('[LookupBadge] ❌ Error:', err);
                        return;
                    }

                    const results = response.data.results || [];
                    results.forEach(function(row) {
                        if (row['id']) {
                            // Changed: store an object in the Map
                            lookupUids.set(row['id'].trim(), {
                                added_by:    (row['added_by']    || '').trim(),
                                description: (row['description'] || '').trim()
                            });
                        }
                    });

                    lookupLoaded = true;
                    console.log('[LookupBadge] ✅ ' + lookupUids.size + ' UIDs loaded');
                }
            );
        });
    }

    fetchLookupUids('flagged_events', 'id', function(err, uids) {
        if (err) return;
        console.log('[LookupTest] Map ready, size:', uids.size);
    });

    // Init
    setupLookupObserver();
    badgeMatchingRows();

    setupSlider();
    setupSwitch();
    setInterval(setupSlider, 500);
    setInterval(setupSwitch, 500);
});
