#!/usr/bin/env python3
import json
import argparse
import os
import gzip

def process_directory(input_dir, output_dir=None):
    """Process all JSON files in a directory"""
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        return

    # Create output directory if specified and doesn't exist
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Find all JSON files (including .json.gz) in the directory
    json_files = []
    for item in os.listdir(input_dir):
        if item.endswith('.json') or item.endswith('.json.gz'):
            json_files.append(os.path.join(input_dir, item))

    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    print(f"Found {len(json_files)} JSON file(s) in {input_dir}")
    print("-" * 50)

    success_count = 0
    for json_file in json_files:
        try:
            # Determine output file path
            if output_dir:
                filename = os.path.basename(json_file)
                # Remove .json.gz or .json extension
                if filename.endswith('.json.gz'):
                    html_filename = filename[:-8] + '_gz_viewer.html'
                else:
                    html_filename = os.path.splitext(filename)[0] + '_viewer.html'
                output_file = os.path.join(output_dir, html_filename)
            else:
                if json_file.endswith('.json.gz'):
                    output_file = json_file[:-8] + '_gz_viewer.html'
                else:
                    output_file = os.path.splitext(json_file)[0] + '_viewer.html'

            generate_html(json_file, output_file)
            success_count += 1
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    print("-" * 50)
    print(f"Successfully processed {success_count}/{len(json_files)} file(s)")

def generate_html(json_file, output_file=None):
    """Generate HTML visualization from JSON data"""
    # Detect if file is gzipped and read accordingly
    if json_file.endswith('.gz'):
        with gzip.open(json_file, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    else:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

    if output_file is None:
        if json_file.endswith('.json.gz'):
            output_file = json_file[:-7] + '_viewer.html'
        else:
            output_file = os.path.splitext(json_file)[0] + '_viewer.html'

    result_set = data.get('Result_Set', [])
    configuration = data.get('configuration', {})
    info_list = data.get('info', [])
    # Handle info field which can be a list with one element
    device_info = info_list[0] if isinstance(info_list, list) and len(info_list) > 0 else info_list if isinstance(info_list, dict) else {}
    device_info_json = json.dumps(device_info) if device_info else '{{}}'

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TMF8829 JSON Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }}

        .controls {{
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 15px;
        }}

        .control-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 5px;
        }}

        .control-row:last-child {{
            margin-bottom: 0;
        }}

        label {{
            font-weight: bold;
            color: #555;
            min-width: 120px;
            font-size: 10px;
        }}

        input[type="range"] {{
            flex: 1;
            max-width: 400px;
        }}

        select {{
            padding: 5px 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
            font-size: 10px;
        }}

        button {{
            padding: 4px 12px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 10px;
        }}

        button:hover {{
            background-color: #45a049;
        }}

        button:disabled {{
            background-color: #cccccc;
            cursor: not-allowed;
        }}

        input[type="checkbox"] {{
            margin-right: 5px;
            cursor: pointer;
        }}

        input[type="checkbox"]:disabled {{
            cursor: not-allowed;
        }}

        .checkbox-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .checkbox-subgroup {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-left: 20px;
        }}

        .checkbox-label {{
            cursor: pointer;
            user-select: none;
            font-size: 10px;
        }}

        .checkbox-label:has(input:disabled) {{
            color: #999;
        }}

        .info {{
            background-color: #e3f2fd;
            padding: 5px 10px;
            border-radius: 5px;
            margin-bottom: 8px;
            color: #1976d2;
            font-size: 10px;
            line-height: 1.2;
        }}

        .info.warning {{
            color: #d32f2f;
            font-weight: bold;
        }}

        .grid-container {{
            overflow: auto;
            border: 2px solid #333;
            border-radius: 5px;
            max-height: 90vh;
        }}

        .grid {{
            display: grid;
            gap: 2px;
            padding: 10px;
            background-color: #fff;
        }}

        .cell {{
            border: 1px solid #999;
            padding: 4px 6px;
            min-width: 80px;
            min-height: 60px;
            background-color: #fafafa;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .cell-header {{
            position: absolute;
            top: 1px;
            right: 3px;
            font-size: 9px;
            color: #666;
        }}

        .cell-data {{
            font-size: 10px;
            line-height: 1.3;
            word-wrap: break-word;
        }}

        .peak {{
            padding: 1px 2px;
            border-radius: 2px;
            margin: 1px 0;
        }}

        .peak-high {{
            color: #006400;
            background-color: #90EE90;
        }}

        .peak-medium {{
            color: #8B4500;
            background-color: #FFD700;
        }}

        .peak-low {{
            color: #8B0000;
            background-color: #FFB6C1;
        }}

        .peak-none {{
            color: #666;
        }}

        .no-data {{
            color: #999;
            font-style: italic;
        }}

        .frame-count {{
            text-align: center;
            color: #666;
            margin-top: 15px;
            font-size: 14px;
        }}

        .legend {{
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .legend-title {{
            font-weight: bold;
            color: #333;
            margin-right: 5px;
        }}

        .legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            margin-left: 10px;
        }}

        .legend-color {{
            width: 30px;
            height: 20px;
            border-radius: 2px;
            padding: 1px 2px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .version-info {{
            background-color: #fff3cd;
            padding: 8px 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #856404;
            font-size: 10px;
        }}

        .histo-container {{
            margin-top: 10px;
            border: 2px solid #333;
            border-radius: 5px;
            padding: 10px;
            background-color: #fff;
        }}

        .histo-header {{
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}

        .histo-grid {{
            display: grid;
            gap: 5px;
            overflow: auto;
            max-height: 730px;
            padding: 5px;
        }}

        .histo-cell {{
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
            background-color: #fafafa;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .histo-cell:hover {{
            transform: scale(1.02);
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            border-color: #4CAF50;
        }}

        .histo-cell-header {{
            font-size: 9px;
            color: #666;
            margin-bottom: 3px;
            font-weight: bold;
        }}

        .histo-chart {{
            width: 120px;
            height: 60px;
        }}

        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            justify-content: center;
            align-items: center;
        }}

        .modal.show {{
            display: flex;
        }}

        .modal-content {{
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            max-width: 95%;
            max-height: 95%;
            overflow-y: auto;
            position: relative;
            display: flex;
            flex-direction: column;
        }}

        .modal-close {{
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 28px;
            cursor: pointer;
            color: #666;
            font-weight: bold;
        }}

        .modal-close:hover {{
            color: #000;
        }}

        .modal-chart-container {{
            width: 800px;
            min-height: 600px;
            overflow-y: auto;
            position: relative;
        }}

        .modal-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            margin-right: 40px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="version-info" id="versionInfo"></div>

        <div class="controls">
            <div class="info" id="frameDetails"></div>

            <div class="control-row">
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="showNoise">
                        Noise
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showXtalk">
                        XTalk
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showPeaks" checked>
                        Peaks
                        <select id="numPeaksSelect" style="margin-left: 8px;">
                        </select>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showDistance" checked>
                            Distance
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSNR" checked>
                            SNR
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSignal">
                            Signal
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showXYZ">
                            XYZ
                        </label>
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showHistogram" disabled>
                        Histogram
                        <select id="histoTypeSelect" style="margin-left: 8px;" disabled>
                            <option value="mp">MP</option>
                            <option value="ref">Ref</option>
                        </select>
                    </label>
                </div>
                <input type="range" id="frameSlider" min="0" max="{len(result_set)-1}" value="0" step="1">
                <span id="frameInfo">0 / {len(result_set)-1}</span>
                <button id="prevBtn" onclick="prevFrame()">◀ Previous</button>
                <button id="nextBtn" onclick="nextFrame()">Next ▶</button>
            </div>
        </div>

        <div class="grid-container">
            <div class="grid" id="dataGrid"></div>
        </div>

        <div class="histo-container" id="histoContainer" style="display: none;">
            <div class="histo-grid" id="histoGrid"></div>
        </div>

        <div class="controls" style="margin-top: 15px;">
            <div class="control-row">
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" id="showNoise2">
                        Noise
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showXtalk2">
                        XTalk
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showPeaks2" checked>
                        Peaks
                        <select id="numPeaksSelect2" style="margin-left: 8px;">
                        </select>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showDistance2" checked>
                            Distance
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSNR2" checked>
                            SNR
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showSignal2">
                            Signal
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" id="showXYZ2">
                            XYZ
                        </label>
                    </label>
                    <label class="checkbox-label">
                        <input type="checkbox" id="showHistogram2" disabled>
                        Histogram
                        <select id="histoTypeSelect2" style="margin-left: 8px;" disabled>
                            <option value="mp">MP</option>
                            <option value="ref">Ref</option>
                        </select>
                    </label>
                </div>
                <input type="range" id="frameSlider2" min="0" max="{len(result_set)-1}" value="0" step="1">
                <span id="frameInfo2">0 / {len(result_set)-1}</span>
                <button id="prevBtn2" onclick="prevFrame()">◀ Previous</button>
                <button id="nextBtn2" onclick="nextFrame()">Next ▶</button>
            </div>
        </div>
    </div>

    <div class="modal" id="histoModal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div class="modal-title" id="modalTitle"></div>
            <div class="modal-chart-container" id="modalChart"></div>
        </div>
    </div>

    <script>
        const data = {json.dumps(result_set)};
        const config = {json.dumps(configuration)};
        const deviceInfo = {device_info_json};
        let currentFrame = 0;
        let numPeaksToShow = config.nr_peaks || 4;
        let hasHistogram = false;

        // Check if data contains histogram for current frame
        function checkHistogramAvailability(frame = null) {{
            // If no frame provided, check first frame for initial state
            if (frame === null) {{
                frame = data[0];
            }}

            hasHistogram = false;

            if (frame) {{
                // Check mp_histo
                if (frame.mp_histo && frame.mp_histo.length > 0) {{
                    // mp_histo[row] is an array of dicts, each with 'bin' key
                    for (let i = 0; i < frame.mp_histo.length; i++) {{
                        const row = frame.mp_histo[i];
                        if (Array.isArray(row) && row.length > 0) {{
                            // Check first item in the row
                            const item = row[0];
                            if (item && item.bin && Array.isArray(item.bin) && item.bin.length > 0) {{
                                hasHistogram = true;
                                break;
                            }}
                        }}
                    }}
                }}

                // Check ref_histo if mp_histo doesn't have data
                if (!hasHistogram && frame.ref_histo && frame.ref_histo.length > 0) {{
                    // ref_histo[row] is a dict with 'bin' key
                    for (let i = 0; i < frame.ref_histo.length; i++) {{
                        const item = frame.ref_histo[i];
                        if (item && item.bin && Array.isArray(item.bin) && item.bin.length > 0) {{
                            hasHistogram = true;
                            break;
                        }}
                    }}
                }}
            }}
            const histogramCheckbox = document.getElementById('showHistogram');
            const histoTypeSelect = document.getElementById('histoTypeSelect');
            const histogramCheckbox2 = document.getElementById('showHistogram2');
            const histoTypeSelect2 = document.getElementById('histoTypeSelect2');

            if (hasHistogram) {{
                histogramCheckbox.disabled = false;
                histoTypeSelect.disabled = false;
                histogramCheckbox2.disabled = false;
                histoTypeSelect2.disabled = false;
            }} else {{
                histogramCheckbox.disabled = true;
                histoTypeSelect.disabled = true;
                histogramCheckbox2.disabled = true;
                histoTypeSelect2.disabled = true;
            }}
        }}

        // Initialize version info
        function initVersionInfo() {{
            const versionDiv = document.getElementById('versionInfo');
            let versionText = 'Version Information: ';

            // Helper function to format version (handle arrays and empty strings)
            function formatVersion(val) {{
                if (!val || (typeof val === 'string' && val.trim() === '')) {{
                    return 'N/A';
                }}
                if (Array.isArray(val)) {{
                    return val.join('.');
                }}
                return val;
            }}

            // Try different possible field names
            const hostVersion = formatVersion(deviceInfo['host version'] || deviceInfo['EVM version'] || deviceInfo['host_version']);
            const fwVersion = formatVersion(deviceInfo['fw version'] || deviceInfo['fw_version']);
            const loggerVersion = formatVersion(deviceInfo['logger version'] || deviceInfo['logger_version']);
            const serialNumber = formatVersion(deviceInfo['serial number'] || deviceInfo['serial_number']);

            versionText += `Host: ${{hostVersion}} | FW: ${{fwVersion}} | Logger: ${{loggerVersion}} | Serial: ${{serialNumber}}`;
            versionDiv.textContent = versionText;
        }}

        // Initialize numPeaksSelect dropdown
        function initNumPeaksSelect() {{
            // Fixed options: 1, 2, 3, 4
            const maxObjects = 4;
            const defaultPeaks = config.nr_peaks || 4;
            const selects = ['numPeaksSelect', 'numPeaksSelect2'];

            selects.forEach(selectId => {{
                const select = document.getElementById(selectId);
                if (!select) return;

                // Clear existing options
                select.innerHTML = '';

                // Add options from 1 to 4
                for (let i = 1; i <= maxObjects; i++) {{
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = i;
                    if (i === defaultPeaks) {{
                        option.selected = true;
                    }}
                    select.appendChild(option);
                }}
            }});

            // Set initial value
            numPeaksToShow = parseInt(document.getElementById('numPeaksSelect').value);
        }}

        // Display options
        let displayOptions = {{
            showNoise: false,
            showPeaks: true,
            showXtalk: false,
            showDistance: true,
            showSNR: true,
            showXYZ: false,
            showSignal: false,
            showHistogram: false,
            histoType: 'mp'
        }};

        // Update peaks options enabled state based on showPeaks checkbox
        function updatePeaksOptionsEnabled() {{
            const showPeaks = document.getElementById('showPeaks').checked;
            const peaksOptions = ['showDistance', 'showSNR', 'showXYZ', 'showSignal', 'numPeaksSelect',
                                  'showDistance2', 'showSNR2', 'showXYZ2', 'showSignal2', 'numPeaksSelect2'];

            peaksOptions.forEach(optId => {{
                const element = document.getElementById(optId);
                element.disabled = !showPeaks;
            }});
        }}

        // Initialize
        initVersionInfo();
        initNumPeaksSelect();
        checkHistogramAvailability();
        updatePeaksOptionsEnabled();
        updateDisplay();

        // Event listeners for top controls
        document.getElementById('frameSlider').addEventListener('input', function(e) {{
            currentFrame = parseInt(e.target.value);
            updateDisplay();
        }});

        // Checkbox event listeners (top)
        document.getElementById('showNoise').addEventListener('change', function(e) {{
            displayOptions.showNoise = e.target.checked;
            syncControl('showNoise2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showPeaks').addEventListener('change', function(e) {{
            displayOptions.showPeaks = e.target.checked;
            syncControl('showPeaks2', e.target.checked);
            updatePeaksOptionsEnabled();
            updateDisplay();
        }});

        document.getElementById('showXtalk').addEventListener('change', function(e) {{
            displayOptions.showXtalk = e.target.checked;
            syncControl('showXtalk2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showDistance').addEventListener('change', function(e) {{
            displayOptions.showDistance = e.target.checked;
            syncControl('showDistance2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showSNR').addEventListener('change', function(e) {{
            displayOptions.showSNR = e.target.checked;
            syncControl('showSNR2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showXYZ').addEventListener('change', function(e) {{
            displayOptions.showXYZ = e.target.checked;
            syncControl('showXYZ2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showSignal').addEventListener('change', function(e) {{
            displayOptions.showSignal = e.target.checked;
            syncControl('showSignal2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('numPeaksSelect').addEventListener('change', function(e) {{
            numPeaksToShow = parseInt(e.target.value);
            document.getElementById('numPeaksSelect2').value = e.target.value;
            updateDisplay();
        }});

        document.getElementById('showHistogram').addEventListener('change', function(e) {{
            displayOptions.showHistogram = e.target.checked;
            syncControl('showHistogram2', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('histoTypeSelect').addEventListener('change', function(e) {{
            displayOptions.histoType = e.target.value;
            document.getElementById('histoTypeSelect2').value = e.target.value;
            updateHistogramDisplay();
        }});

        // Event listeners for bottom controls (synced with top)
        document.getElementById('frameSlider2').addEventListener('input', function(e) {{
            currentFrame = parseInt(e.target.value);
            updateDisplay();
        }});

        // Checkbox event listeners (bottom)
        document.getElementById('showNoise2').addEventListener('change', function(e) {{
            displayOptions.showNoise = e.target.checked;
            syncControl('showNoise', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showPeaks2').addEventListener('change', function(e) {{
            displayOptions.showPeaks = e.target.checked;
            syncControl('showPeaks', e.target.checked);
            updatePeaksOptionsEnabled();
            updateDisplay();
        }});

        document.getElementById('showXtalk2').addEventListener('change', function(e) {{
            displayOptions.showXtalk = e.target.checked;
            syncControl('showXtalk', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showDistance2').addEventListener('change', function(e) {{
            displayOptions.showDistance = e.target.checked;
            syncControl('showDistance', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showSNR2').addEventListener('change', function(e) {{
            displayOptions.showSNR = e.target.checked;
            syncControl('showSNR', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showXYZ2').addEventListener('change', function(e) {{
            displayOptions.showXYZ = e.target.checked;
            syncControl('showXYZ', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('showSignal2').addEventListener('change', function(e) {{
            displayOptions.showSignal = e.target.checked;
            syncControl('showSignal', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('numPeaksSelect2').addEventListener('change', function(e) {{
            numPeaksToShow = parseInt(e.target.value);
            document.getElementById('numPeaksSelect').value = e.target.value;
            updateDisplay();
        }});

        document.getElementById('showHistogram2').addEventListener('change', function(e) {{
            displayOptions.showHistogram = e.target.checked;
            syncControl('showHistogram', e.target.checked);
            updateDisplay();
        }});

        document.getElementById('histoTypeSelect2').addEventListener('change', function(e) {{
            displayOptions.histoType = e.target.value;
            document.getElementById('histoTypeSelect').value = e.target.value;
            updateHistogramDisplay();
        }});

        // Helper function to sync controls
        function syncControl(targetId, checked) {{
            const target = document.getElementById(targetId);
            if (target) {{
                target.checked = checked;
            }}
        }}

        function updateDisplay() {{
            const frame = data[currentFrame];
            const grid = document.getElementById('dataGrid');
            const frameSlider = document.getElementById('frameSlider');
            const frameSlider2 = document.getElementById('frameSlider2');
            const frameInfo = document.getElementById('frameInfo');
            const frameInfo2 = document.getElementById('frameInfo2');
            const frameDetails = document.getElementById('frameDetails');

            // Check histogram availability for current frame
            checkHistogramAvailability(frame);

            // Update sliders and info
            frameSlider.value = currentFrame;
            frameSlider2.value = currentFrame;
            frameInfo.textContent = `${{currentFrame}} / ${{data.length - 1}}`;
            frameInfo2.textContent = `${{currentFrame}} / ${{data.length - 1}}`;

            // Get resolution from current frame
            let resolution = 'N/A';
            if (frame.results && frame.results.length > 0) {{
                const rows = frame.results.length;
                const cols = frame.results[0] ? frame.results[0].length : 0;
                resolution = `${{cols}}x${{rows}}`;
            }}

            // Update frame details with resolution
            if (frame.info) {{
                const iterations = config.iterations || 'N/A';
                const period = config.period || 'N/A';
                const confThresh = config.confidence_threshold || 'N/A';
                const readTime = frame.info.read_time || frame.info.systick_t0 || 'N/A';
                const haIterations = config.high_accuracy_iterations || 'N/A';
                const warningText = (frame.info.warnings > 0) ? '⚠️ Frame has warnings | ' : '';

                frameDetails.innerHTML = `${{warningText}}Frame: ${{frame.info.frame_number || 'N/A'}} | ` +
                    `Res: ${{resolution}} | ` +
                    `Iterations: ${{iterations}}k | ` +
                    `HA_Iterations: ${{haIterations}}k | ` +
                    `Period: ${{period}}ms | ` +
                    `Conf Thresh: ${{confThresh}} | ` +
                    `Temp: ${{frame.info.temperature}}°C | ` +
                    `ReadTime: ${{readTime}} | ` +
                    `<span class="legend-item"><span class="legend-color peak-high">c>20</span></span>` +
                    `<span class="legend-item"><span class="legend-color peak-medium">20≥c>10</span></span>` +
                    `<span class="legend-item"><span class="legend-color peak-low">10≥c>0</span></span>`;

                // Add warning class if frame has warnings
                if (frame.info.warnings > 0) {{
                    frameDetails.classList.add('warning');
                }} else {{
                    frameDetails.classList.remove('warning');
                }}
            }} else {{
                frameDetails.textContent = `Resolution: ${{resolution}} | Frame info not available`;
            }}

            // Clear grid
            grid.innerHTML = '';

            if (!frame.results) {{
                grid.innerHTML = '<div style="padding: 20px; color: #999;">No results data available</div>';
                return;
            }}

            // Determine resolution from current frame
            let rows = frame.results.length;
            let cols = frame.results[0] ? frame.results[0].length : 0;

            // Set grid layout
            grid.style.gridTemplateColumns = `repeat(${{cols}}, 1fr)`;

            // Create cells
            for (let row = 0; row < rows; row++) {{
                for (let col = 0; col < cols; col++) {{
                    const cell = document.createElement('div');
                    cell.className = 'cell';

                    const header = document.createElement('div');
                    header.className = 'cell-header';
                    header.textContent = `(${{col}},${{row}})`;
                    cell.appendChild(header);

                    const dataDiv = document.createElement('div');
                    dataDiv.className = 'cell-data';

                    if (frame.results[row] && frame.results[row][col]) {{
                        const cellData = frame.results[row][col];
                        let hasData = false;

                        // Display Noise
                        if (displayOptions.showNoise && 'noise' in cellData) {{
                            const noiseDiv = document.createElement('div');
                            noiseDiv.className = 'peak';
                            noiseDiv.style.color = '#666';
                            noiseDiv.style.background = '#e0e0e0';
                            noiseDiv.textContent = `Noise: ${{cellData.noise}}`;
                            dataDiv.appendChild(noiseDiv);
                            hasData = true;
                        }}

                        // Display Peaks
                        if (displayOptions.showPeaks && cellData.peaks && cellData.peaks.length > 0) {{
                            // Use numPeaksToShow from dropdown to determine how many peaks to show
                            cellData.peaks.slice(0, numPeaksToShow).forEach((peak, peakIndex) => {{
                                const peakDiv = document.createElement('div');
                                peakDiv.className = 'peak';

                                const distance = peak.distance;
                                const snr = peak.snr;
                                const signal = peak.signal;
                                const x = peak.x;
                                const y = peak.y;
                                const z = peak.z;

                                // Determine color based on SNR
                                let peakClass = 'peak-none';
                                if (snr > 20) peakClass = 'peak-high';
                                else if (snr > 10) peakClass = 'peak-medium';
                                else if (snr > 0) peakClass = 'peak-low';

                                peakDiv.classList.add(peakClass);

                                const peakNum = peakIndex + 1;

                                // Build text with each field on a separate line, right-aligned to 7 chars
                                let peakLines = [];

                                if (displayOptions.showDistance) {{
                                    const distanceText = `${{distance}}`;
                                    const padding = ' '.repeat(Math.max(0, 7 - distanceText.length));
                                    peakLines.push(`d${{peakNum}}:${{padding}}${{distanceText}}`);
                                }}
                                if (displayOptions.showSNR) {{
                                    const snrText = `${{snr}}`;
                                    const padding = ' '.repeat(Math.max(0, 7 - snrText.length));
                                    peakLines.push(`c${{peakNum}}:${{padding}}${{snrText}}`);
                                }}
                                if (displayOptions.showSignal) {{
                                    const signalText = `${{signal}}`;
                                    const padding = ' '.repeat(Math.max(0, 7 - signalText.length));
                                    peakLines.push(`s${{peakNum}}:${{padding}}${{signalText}}`);
                                }}
                                if (displayOptions.showXYZ) {{
                                    const xNum = parseFloat(x);
                                    const yNum = parseFloat(y);
                                    const zNum = parseFloat(z);
                                    const xText = xNum.toFixed(1);
                                    const yText = yNum.toFixed(1);
                                    const zText = zNum.toFixed(1);
                                    const xPadding = ' '.repeat(Math.max(0, 7 - xText.length));
                                    const yPadding = ' '.repeat(Math.max(0, 7 - yText.length));
                                    const zPadding = ' '.repeat(Math.max(0, 7 - zText.length));
                                    peakLines.push(`x${{peakNum}}:${{xPadding}}${{xText}}`);
                                    peakLines.push(`y${{peakNum}}:${{yPadding}}${{yText}}`);
                                    peakLines.push(`z${{peakNum}}:${{zPadding}}${{zText}}`);
                                }}

                                peakDiv.innerHTML = peakLines.join('<br>');
                                dataDiv.appendChild(peakDiv);
                                hasData = true;
                            }});
                        }}

                        // Display XTalk
                        if (displayOptions.showXtalk && 'xtalk' in cellData) {{
                            const xtalkDiv = document.createElement('div');
                            xtalkDiv.className = 'peak';
                            xtalkDiv.style.color = '#6b3fa0';
                            xtalkDiv.style.background = '#e1bee7';
                            xtalkDiv.textContent = `XTalk: ${{cellData.xtalk}}`;
                            dataDiv.appendChild(xtalkDiv);
                            hasData = true;
                        }}

                        if (!hasData) {{
                            dataDiv.innerHTML = '<div class="no-data">No data</div>';
                        }}
                    }} else {{
                        dataDiv.innerHTML = '<div class="no-data">No data</div>';
                    }}

                    cell.appendChild(dataDiv);
                    grid.appendChild(cell);
                }}
            }}

            // Update histogram display
            updateHistogramDisplay();
        }}

        // Create histogram chart using simple SVG
        function createHistogramChart(bins, width, height, color = '#4CAF50', showTicks = false) {{
            if (!bins || bins.length === 0) {{
                return `<div style="width:${{width}}px;height:${{height}}px;display:flex;align-items:center;justify-content:center;color:#999;">No data</div>`;
            }}

            const maxValue = Math.max(...bins);
            // Use smaller padding for thumbnails, larger for detailed charts
            const padding = showTicks ? 45 : 15;
            const chartWidth = width - padding * 2;
            const chartHeight = height - padding * 2;
            const barWidth = chartWidth / bins.length;
            const barGap = Math.max(0.5, barWidth * 0.1);
            const actualBarWidth = Math.max(1, barWidth - barGap);

            let svg = `<svg width="${{width}}" height="${{height}}" xmlns="http://www.w3.org/2000/svg">`;

            // Y-axis
            svg += `<line x1="${{padding}}" y1="${{padding}}" x2="${{padding}}" y2="${{height - padding}}" stroke="#333" stroke-width="1"/>`;

            // X-axis
            svg += `<line x1="${{padding}}" y1="${{height - padding}}" x2="${{width - padding}}" y2="${{height - padding}}" stroke="#333" stroke-width="1"/>`;

            // Bars
            bins.forEach((value, index) => {{
                const barHeight = maxValue > 0 ? (value / maxValue) * chartHeight : 0;
                const x = padding + index * barWidth;
                const y = height - padding - barHeight;

                if (barHeight > 0) {{
                    svg += `<rect x="${{x}}" y="${{y}}" width="${{actualBarWidth}}" height="${{barHeight}}" fill="${{color}}" stroke="#333" stroke-width="0.5"/>`;
                }}
            }});

            // X-axis ticks and labels
            if (showTicks) {{
                const xTickCount = Math.min(10, bins.length);
                const xTickStep = Math.ceil(bins.length / xTickCount);
                for (let i = 0; i <= bins.length; i += xTickStep) {{
                    const x = padding + i * barWidth;
                    svg += `<line x1="${{x}}" y1="${{height - padding}}" x2="${{x}}" y2="${{height - padding + 3}}" stroke="#333" stroke-width="1"/>`;
                    svg += `<text x="${{x}}" y="${{height - padding + 15}}" text-anchor="middle" font-size="10" fill="#666">${{i}}</text>`;
                }}
            }}

            // Y-axis ticks and labels
            if (showTicks) {{
                const yTickCount = 5;
                for (let i = 0; i <= yTickCount; i++) {{
                    const value = Math.round((maxValue / yTickCount) * i);
                    const y = height - padding - (value / maxValue) * chartHeight;
                    svg += `<line x1="${{padding - 3}}" y1="${{y}}" x2="${{padding}}" y2="${{y}}" stroke="#333" stroke-width="1"/>`;
                    svg += `<text x="${{padding - 5}}" y="${{y + 3}}" text-anchor="end" font-size="10" fill="#666">${{value}}</text>`;
                }}
            }}

            // Axis labels
            svg += `<text x="${{width / 2}}" y="${{height - 5}}" text-anchor="middle" font-size="10" fill="#666">bin</text>`;
            svg += `<text x="${{5}}" y="${{height / 2}}" text-anchor="middle" font-size="10" fill="#666" transform="rotate(-90, ${{5}}, ${{height / 2}})">count</text>`;

            svg += `</svg>`;
            return svg;
        }}

        // Update histogram display
        function updateHistogramDisplay() {{
            const frame = data[currentFrame];
            const histoContainer = document.getElementById('histoContainer');
            const histoGrid = document.getElementById('histoGrid');

            if (!displayOptions.showHistogram || !hasHistogram) {{
                histoContainer.style.display = 'none';
                return;
            }}

            histoContainer.style.display = 'block';
            histoGrid.innerHTML = '';

            // Get resolution from results
            let rows = 0;
            let cols = 0;
            if (frame.results && frame.results.length > 0) {{
                rows = frame.results.length;
                cols = frame.results[0] ? frame.results[0].length : 0;
            }}

            const histoType = displayOptions.histoType;

            // Set grid layout to match resolution
            histoGrid.style.gridTemplateColumns = `repeat(${{cols}}, 1fr)`;

            // Create cells for each position (row, col)
            for (let row = 0; row < rows; row++) {{
                for (let col = 0; col < cols; col++) {{
                    const cell = document.createElement('div');
                    cell.className = 'histo-cell';

                    const header = document.createElement('div');
                    header.className = 'histo-cell-header';
                    header.textContent = `(${{col}},${{row}})`;
                    cell.appendChild(header);

                    const chartContainer = document.createElement('div');
                    chartContainer.className = 'histo-chart';

                    let binData = [];
                    let color = '#999';

                    if (histoType === 'mp') {{
                        // Get histogram from mp_histo[row][col]
                        if (frame.mp_histo && frame.mp_histo[row] && frame.mp_histo[row][col]) {{
                            const histoData = frame.mp_histo[row][col];
                            if (histoData && histoData.bin && Array.isArray(histoData.bin)) {{
                                binData = histoData.bin;
                            }}
                            color = '#4CAF50';
                        }}
                    }} else if (histoType === 'ref') {{
                        // Get histogram from ref_histo[row] (one per row, not per column)
                        if (frame.ref_histo && frame.ref_histo[row]) {{
                            const histoData = frame.ref_histo[row];
                            if (histoData && histoData.bin && Array.isArray(histoData.bin)) {{
                                binData = histoData.bin;
                            }}
                            color = '#2196F3';
                        }}
                    }}

                    if (binData.length > 0) {{
                        chartContainer.innerHTML = createHistogramChart(binData, 120, 60, color);
                        // Add click event to open modal
                        cell.onclick = () => openModal(histoType.toUpperCase(), row, col, binData, color);
                    }} else {{
                        chartContainer.innerHTML = '<div style="width:120px;height:60px;display:flex;align-items:center;justify-content:center;color:#999;font-size:9px;">No data</div>';
                    }}

                    cell.appendChild(chartContainer);
                    histoGrid.appendChild(cell);
                }}
            }}
        }}

        // Open modal with enlarged histogram
        function openModal(type, row, col, bins, color) {{
            const modal = document.getElementById('histoModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalChart = document.getElementById('modalChart');

            const frame = data[currentFrame];

            modalTitle.textContent = `${{type}} Histogram (${{col}},${{row}})`;

            // Create chart with ticks
            modalChart.innerHTML = createHistogramChart(bins, 800, 600, color, true);

            // Add annotation for highest peak (bin and count)
            if (bins && bins.length > 0) {{
                let maxCount = 0;
                let maxBinIndex = 0;

                // Find the highest peak
                bins.forEach((value, index) => {{
                    if (value > maxCount) {{
                        maxCount = value;
                        maxBinIndex = index;
                    }}
                }});

                // Calculate position for annotation
                const width = 800;
                const height = 600;
                const padding = 45;
                const chartWidth = width - padding * 2;
                const chartHeight = height - padding * 2;
                const barWidth = chartWidth / bins.length;

                const x = padding + maxBinIndex * barWidth + barWidth / 2;
                const y = height - padding - (maxCount / Math.max(...bins)) * chartHeight;

                // Add annotation on top of the highest peak
                const annotation = `<div style="
                    position: absolute;
                    left: ${{x}}px;
                    top: ${{y - 35}}px;
                    transform: translateX(-50%);
                    background-color: #ffeb3b;
                    color: #333;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    white-space: nowrap;
                    z-index: 10;
                ">bin: ${{maxBinIndex}}, count: ${{maxCount}}</div>`;

                modalChart.innerHTML += annotation;
            }}

            // Add distance and SNR information
            let peakInfo = '';
            if (frame.results && frame.results[row] && frame.results[row][col]) {{
                const cellData = frame.results[row][col];
                if (cellData.peaks && cellData.peaks.length > 0) {{
                    peakInfo = '<div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; font-size: 12px;">';
                    peakInfo += '<strong>Peak Information:</strong><br><br>';

                    cellData.peaks.forEach((peak, idx) => {{
                        const distance = peak.distance;
                        const snr = peak.snr;

                        const distanceText = `${{distance}}`;

                        peakInfo += `<span style="color: ${{snr > 20 ? '#006400' : snr > 10 ? '#8B4500' : '#8B0000'}};">`;
                        peakInfo += `<strong>Peak ${{idx + 1}}:</strong> Distance = ${{distanceText}}, SNR = ${{snr}}</span><br>`;
                    }});

                    peakInfo += '</div>';
                }}
            }}

            if (peakInfo) {{
                modalChart.innerHTML += peakInfo;
            }}

            modal.classList.add('show');
        }}

        // Close modal
        function closeModal() {{
            const modal = document.getElementById('histoModal');
            modal.classList.remove('show');
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('histoModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}

        function prevFrame() {{
            if (currentFrame > 0) {{
                currentFrame--;
                updateDisplay();
            }}
        }}

        function nextFrame() {{
            if (currentFrame < data.length - 1) {{
                currentFrame++;
                updateDisplay();
            }}
        }}

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowLeft') prevFrame();
            if (e.key === 'ArrowRight') nextFrame();
            if (e.key === 'Home') {{
                currentFrame = 0;
                updateDisplay();
            }}
            if (e.key === 'End') {{
                currentFrame = data.length - 1;
                updateDisplay();
            }}
        }});
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML viewer generated: {output_file}")
    print(f"Total frames: {len(result_set)}")
    print("Open the HTML file in a web browser to view the data.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate HTML visualization from TMF8829 JSON log')
    parser.add_argument('-i', '--input', required=True, help='Path to JSON file (or .json.gz) or directory containing JSON files')
    parser.add_argument('-o', '--output', help='Output HTML file path or directory (optional)')
    args = parser.parse_args()

    # Check if -i is a directory or a file
    if os.path.isdir(args.input):
        process_directory(args.input, args.output)
    elif os.path.isfile(args.input):
        generate_html(args.input, args.output)
    else:
        print(f"Error: {args.input} is not a valid file or directory")
