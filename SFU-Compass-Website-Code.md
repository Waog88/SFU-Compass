<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SFU AQ Campus Map & Kiosk Directory</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- FontAwesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            sfu: {
              red: '#A6192E',
              darkRed: '#7A0010',
              accent: '#CC0000',
              gold: '#E5A823'
            },
            dark: {
              bg: '#0F172A',
              card: '#1E293B',
              border: '#334155'
            }
          }
        }
      }
    }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    body {
      font-family: 'Inter', sans-serif;
    }
    .font-mono {
      font-family: 'JetBrains Mono', monospace;
    }
    
    /* Dynamic Animated Glowing Path */
    .path-glow {
      stroke-dasharray: 12, 6;
      animation: dash 1.2s linear infinite, glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes dash {
      to {
        stroke-dashoffset: -36;
      }
    }
    
    @keyframes glow {
      from {
        filter: drop-shadow(0 0 3px rgba(204, 0, 0, 0.6));
      }
      to {
        filter: drop-shadow(0 0 8px rgba(255, 60, 60, 0.9));
      }
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
      background: #334155;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #a6192e;
    }
  </style>
</head>
<body class="bg-dark-bg text-slate-100 min-h-screen flex flex-col overflow-x-hidden selection:bg-sfu-red selection:text-white">

  <header class="bg-dark-card border-b border-dark-border px-6 py-3 flex items-center justify-between sticky top-0 z-50 shadow-lg">
    <div class="flex items-center space-x-4">
      <div class="bg-sfu-red text-white p-2.5 rounded-xl font-bold text-xl tracking-wider shadow-md shadow-sfu-red/30 flex items-center gap-2">
        <i class="fa-solid fa-compass"></i> SFU AQ NAV
      </div>
      <div>
        <h1 class="font-bold text-lg leading-none text-white">Academic Quadrangle Kiosk</h1>
        <p class="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
          Burnaby Campus • Level 3000 Main Kiosk
        </p>
      </div>
    </div>

    <!-- Status Badges & Hardware Web Serial Connect Button -->
    <div class="hidden md:flex items-center space-x-4">
      <button id="webSerialConnectBtn" class="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-xs px-3.5 py-2 rounded-lg border border-dark-border text-slate-200 transition font-mono">
        <i class="fa-solid fa-plug text-emerald-400"></i> Connect USB Arduino
      </button>
      <div class="flex items-center gap-3 bg-slate-900/80 px-3.5 py-1.5 rounded-lg border border-dark-border">
        <i class="fa-solid fa-microchip text-sfu-red text-lg"></i>
        <div class="text-xs">
          <div class="text-slate-400">Hardware Link</div>
          <div id="hardwareStatus" class="font-mono text-emerald-400 font-semibold">STANDALONE / SIM</div>
        </div>
      </div>
      <div class="flex items-center gap-3 bg-slate-900/80 px-3.5 py-1.5 rounded-lg border border-dark-border">
        <i class="fa-solid fa-wheelchair text-blue-400 text-lg"></i>
        <div class="text-xs">
          <div class="text-slate-400">Accessibility</div>
          <div id="accStatus" class="font-semibold text-slate-300">Standard Route</div>
        </div>
      </div>
    </div>
  </header>

  <main class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 lg:p-6 max-w-[1920px] mx-auto w-full">
    
    <!-- LEFT PANEL: Room Selector & Turn-by-Turn Steps (4 Columns) -->
    <div class="lg:col-span-4 flex flex-col space-y-4">
      
      <!-- Destination Selection Card -->
      <div class="bg-dark-card border border-dark-border rounded-2xl p-5 shadow-xl">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-slate-100 flex items-center gap-2">
            <i class="fa-solid fa-location-dot text-sfu-red"></i> Select Destination
          </h2>
          <span class="text-xs bg-sfu-red/20 text-sfu-red border border-sfu-red/30 px-2.5 py-1 rounded-full font-medium">
            Start: AQ Kiosk (Node 0)
          </span>
        </div>

        <div class="space-y-3">
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400">Target Classroom / Landmark</label>
          <div class="relative">
            <select id="roomSelect" class="w-full bg-slate-900 border border-dark-border rounded-xl px-4 py-3 text-slate-100 font-medium focus:outline-none focus:border-sfu-red focus:ring-1 focus:ring-sfu-red appearance-none transition cursor-pointer">
              <!-- Options populated dynamically by JavaScript -->
            </select>
            <i class="fa-solid fa-chevron-down absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"></i>
          </div>

          <!-- Accessible Route Toggle Switch -->
          <div class="flex items-center justify-between pt-2">
            <label for="accessibleToggle" class="text-sm font-medium text-slate-300 flex items-center gap-2 cursor-pointer">
              <i class="fa-solid fa-universal-access text-blue-400 text-base"></i> Accessible Route
              <span class="text-xs text-slate-500 font-normal">(Ramps & Elevators Only)</span>
            </label>
            <input type="checkbox" id="accessibleToggle" class="w-5 h-5 accent-sfu-red rounded cursor-pointer transition">
          </div>

          <!-- Route Trigger Button -->
          <button id="calcRouteBtn" class="w-full bg-sfu-red hover:bg-sfu-accent text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-sfu-red/30 flex items-center justify-center gap-2 transition active:scale-[0.99] mt-3">
            <i class="fa-solid fa-route"></i> Calculate & Draw Route
          </button>
        </div>
      </div>

      <!-- Turn-by-Turn Guidance Steps -->
      <div class="bg-dark-card border border-dark-border rounded-2xl p-5 shadow-xl flex-1 flex flex-col min-h-[300px]">
        <div class="flex items-center justify-between border-b border-dark-border pb-3 mb-3">
          <h2 class="font-bold text-slate-100 flex items-center gap-2">
            <i class="fa-solid fa-list-ol text-sfu-gold"></i> Step-by-Step Directions
          </h2>
          <div id="routeSummary" class="text-xs font-mono text-slate-400">
            0 steps • 0m
          </div>
        </div>

        <div id="stepsContainer" class="flex-1 overflow-y-auto space-y-3 pr-1">
          <div class="text-center py-10 text-slate-500">
            <i class="fa-solid fa-map-pin text-3xl mb-2 opacity-50"></i>
            <p class="text-sm">Select a destination above to see step-by-step guidance.</p>
          </div>
        </div>
      </div>

      <!-- Hardware Serial Simulator & Monitor Drawer -->
      <div class="bg-dark-card border border-dark-border rounded-2xl p-4 shadow-xl">
        <button id="toggleHardwareBtn" class="w-full flex items-center justify-between text-xs font-mono text-slate-400 hover:text-slate-200">
          <span class="flex items-center gap-2"><i class="fa-solid fa-terminal text-emerald-400"></i> Arduino Hardware Console & Simulator</span>
          <i id="hwChevron" class="fa-solid fa-chevron-up"></i>
        </button>

        <div id="hardwarePanel" class="mt-3 space-y-3">
          <p class="text-xs text-slate-400">Simulate buttons or rotary encoder input from your Grove LCD physical kiosk:</p>
          <div class="grid grid-cols-2 gap-2">
            <button id="simPrevBtn" class="bg-slate-800 hover:bg-slate-700 text-xs py-2 rounded-lg border border-dark-border transition">
              <i class="fa-solid fa-arrow-left"></i> LCD Prev Room
            </button>
            <button id="simNextBtn" class="bg-slate-800 hover:bg-slate-700 text-xs py-2 rounded-lg border border-dark-border transition">
              LCD Next Room <i class="fa-solid fa-arrow-right"></i>
            </button>
          </div>
          <button id="simSelectBtn" class="w-full bg-slate-800 hover:bg-slate-700 text-xs py-2 rounded-lg border border-dark-border text-sfu-gold font-semibold transition">
            <i class="fa-solid fa-circle-check"></i> Simulate Click Select
          </button>

          <!-- Raw Serial Terminal Monitor Output -->
          <div>
            <div class="text-[10px] font-mono text-slate-500 mb-1">SERIAL PAYLOAD (JSON STREAM):</div>
            <pre id="serialLog" class="bg-slate-950 text-emerald-400 font-mono text-[11px] p-2.5 rounded-lg border border-slate-800 h-24 overflow-y-auto whitespace-pre-wrap select-all">// Serial monitor ready...</pre>
          </div>
        </div>
      </div>

    </div>

    <!-- RIGHT PANEL: SVG Campus Floor Map (8 Columns) -->
    <div class="lg:col-span-8 flex flex-col">
      <div class="bg-dark-card border border-dark-border rounded-2xl p-4 lg:p-6 shadow-xl flex-1 flex flex-col relative overflow-hidden min-h-[500px]">
        
        <!-- Map Header & Legends -->
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4 z-10">
          <div>
            <h2 class="font-bold text-slate-100 text-lg flex items-center gap-2">
              <i class="fa-solid fa-map text-sfu-red"></i> SFU Academic Quadrangle Map View
            </h2>
            <p class="text-xs text-slate-400">Level 3000 & 4000 Corridors • Interactive Node Network</p>
          </div>

          <div class="flex items-center space-x-4 text-xs">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-sfu-red inline-block"></span> Dynamic Path</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-blue-500 inline-block"></span> Elevator</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> Kiosk (Start)</span>
          </div>
        </div>

        <!-- SVG Blueprint Map Canvas -->
        <div class="flex-1 bg-slate-950 rounded-xl border border-slate-800 relative flex items-center justify-center p-2 overflow-hidden shadow-inner">
          
          <svg id="aqMapSvg" class="w-full h-full max-h-[720px] select-none" viewBox="0 0 900 650" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#CC0000" />
              </marker>
            </defs>

            <!-- SFU AQ Layout Blueprint Shapes -->
            <g id="aqBlueprintLayer" stroke="#1E293B" stroke-width="2" fill="none">
              <rect x="100" y="50" width="700" height="550" rx="16" fill="#0F172A" opacity="0.6"/>
              <rect x="260" y="170" width="380" height="310" rx="12" fill="#020617" stroke="#334155" stroke-dasharray="4,4"/>
              <text x="450" y="320" fill="#475569" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle">SFU AQ CENTRAL REFLECTING POOL</text>
              <text x="450" y="340" fill="#334155" font-size="11" text-anchor="middle">Level 3000 Outdoor Courtyard</text>
            </g>

            <!-- Static Network Edges -->
            <g id="edgesLayer" stroke="#334155" stroke-width="6" stroke-linecap="round" opacity="0.8">
              <!-- Rendered dynamically by JavaScript -->
            </g>

            <!-- Active Calculated Dynamic Route Line -->
            <g id="activePathLayer">
              <!-- Animated Glowing Lines rendered by JavaScript -->
            </g>

            <!-- Interactive Map Node Circles -->
            <g id="nodesLayer">
              <!-- Interactive Circles & Labels rendered by JavaScript -->
            </g>
          </svg>

          <!-- Hover Tooltip -->
          <div id="mapTooltip" class="absolute pointer-events-none bg-slate-900 border border-slate-700 text-xs px-3 py-1.5 rounded-lg shadow-xl hidden z-20">
            <span id="tooltipName" class="font-bold text-slate-200"></span>
            <div id="tooltipDesc" class="text-[10px] text-slate-400"></div>
          </div>
        </div>

        <!-- Footer Info Bar -->
        <div class="flex items-center justify-between text-xs text-slate-400 mt-3 pt-2 border-t border-dark-border">
          <span id="activeDestinationText"><i class="fa-solid fa-circle-info text-sfu-red"></i> Ready for navigation input.</span>
          <span class="font-mono text-[11px] text-slate-500">SFU HACKATHON BUILD • v1.3</span>
        </div>

      </div>
    </div>

  </main>

  <script>
    /* =========================================================================
       1. MAP DATA GRAPH STRUCTURE (SFU AQ LOCATIONS & WEIGHTED EDGES)
       ========================================================================= */
    const nodes = [
      { id: 0, name: "AQ Kiosk / South Entrance", x: 450, y: 530, level: "3000", type: "kiosk", desc: "Main Kiosk Terminal (You are here)" },
      { id: 1, name: "AQ 3000 North Hallway", x: 450, y: 120, level: "3000", type: "hallway", desc: "North Corridor Junction" },
      { id: 2, name: "AQ 3150 Lecture Hall", x: 680, y: 120, level: "3000", type: "room", desc: "Main Lecture Theatre (Cap: 250)" },
      { id: 3, name: "AQ 3005 Classroom", x: 220, y: 120, level: "3000", type: "room", desc: "Level 3000 Seminar Room" },
      { id: 4, name: "AQ 3000 West Corridor", x: 180, y: 320, level: "3000", type: "hallway", desc: "West Wing Connection" },
      { id: 5, name: "Image Arts Hallway", x: 180, y: 480, level: "3000", type: "room", desc: "School for the Contemporary Arts" },
      { id: 6, name: "AQ 3000 East Corridor", x: 720, y: 320, level: "3000", type: "hallway", desc: "East Wing Connection" },
      { id: 7, name: "Shrum Science Connector", x: 720, y: 480, level: "3000", type: "room", desc: "Access to Shrum Chemistry & Physics" },
      { id: 8, name: "West Central Stairs", x: 220, y: 220, level: "3000-4000", type: "stairs", desc: "Stairs to Level 4000 (Non-Accessible)" },
      { id: 9, name: "AQ Central Elevator", x: 680, y: 220, level: "3000-4000", type: "elevator", desc: "Accessible Elevator to all Levels" },
      { id: 10, name: "AQ 4120 Seminar Room", x: 680, y: 60, level: "4000", type: "room", desc: "Level 4000 Humanities Wing" },
      { id: 11, name: "AQ 4000 West Wing", x: 180, y: 60, level: "4000", type: "room", desc: "Level 4000 Faculty Offices" }
    ];

    // Format: [fromNodeId, toNodeId, distanceMeters, isStairs, textInstruction]
    const edges = [
      [0, 4, 25, false, "Walk WEST along Level 3000 South Concourse"],
      [0, 6, 25, false, "Walk EAST along Level 3000 South Concourse"],
      [4, 5, 20, false, "Continue SOUTH down West Corridor toward Image Arts"],
      [4, 8, 15, false, "Turn NORTH towards West Central Stairs"],
      [4, 3, 30, false, "Follow West Corridor NORTH towards AQ 3005"],
      [3, 1, 20, false, "Turn EAST along North Hallway"],
      [1, 2, 25, false, "Continue EAST down North Hallway toward AQ 3150"],
      [6, 7, 20, false, "Head SOUTH toward Shrum Science Connector"],
      [6, 9, 15, false, "Turn NORTH towards Central Elevator"],
      [6, 2, 30, false, "Follow East Corridor NORTH towards AQ 3150"],
      [8, 11, 15, true, "Climb WEST STAIRS UP to Level 4000"],
      [9, 10, 15, false, "Take CENTRAL ELEVATOR UP to Level 4000"],
      [11, 10, 45, false, "Walk EAST across Level 4000 Concourse"]
    ];

    /* =========================================================================
       2. DIJKSTRA PATHFINDING ALGORITHM
       ========================================================================= */
    function calculateShortestPath(startId, targetId, accessibleOnly = false) {
      const distances = {};
      const previous = {};
      const unvisited = new Set();

      nodes.forEach(node => {
        distances[node.id] = Infinity;
        previous[node.id] = null;
        unvisited.add(node.id);
      });

      distances[startId] = 0;

      while (unvisited.size > 0) {
        let currentId = null;
        unvisited.forEach(id => {
          if (currentId === null || distances[id] < distances[currentId]) {
            currentId = id;
          }
        });

        if (currentId === null || distances[currentId] === Infinity) break;
        if (currentId === targetId) break;

        unvisited.delete(currentId);

        edges.forEach(([u, v, dist, isStairs]) => {
          if (accessibleOnly && isStairs) return;

          let neighborId = null;
          if (u === currentId && unvisited.has(v)) neighborId = v;
          if (v === currentId && unvisited.has(u)) neighborId = u;

          if (neighborId !== null) {
            const alt = distances[currentId] + dist;
            if (alt < distances[neighborId]) {
              distances[neighborId] = alt;
              previous[neighborId] = { id: currentId, edgeDist: dist, isStairs };
            }
          }
        });
      }

      const pathNodes = [];
      const stepInstructions = [];
      let totalDistance = 0;
      let curr = targetId;

      if (distances[targetId] === Infinity) {
        return { pathNodes: [], stepInstructions: [], totalDistance: 0 };
      }

      while (curr !== null) {
        pathNodes.unshift(curr);
        const prevInfo = previous[curr];
        if (prevInfo) {
          totalDistance += prevInfo.edgeDist;
          const edgeData = edges.find(e => (e[0] === prevInfo.id && e[1] === curr) || (e[1] === prevInfo.id && e[0] === curr));
          stepInstructions.unshift({
            text: edgeData ? edgeData[4] : "Proceed to next corridor",
            dist: prevInfo.edgeDist,
            isStairs: prevInfo.isStairs,
            targetNodeName: nodes.find(n => n.id === curr).name
          });
          curr = prevInfo.id;
        } else {
          curr = null;
        }
      }

      return { pathNodes, stepInstructions, totalDistance };
    }

    /* =========================================================================
       3. MAP GRAPHICS ENGINE & DOM BINDINGS
       ========================================================================= */
    const svgMap = document.getElementById('aqMapSvg');
    const edgesLayer = document.getElementById('edgesLayer');
    const activePathLayer = document.getElementById('activePathLayer');
    const nodesLayer = document.getElementById('nodesLayer');
    const roomSelect = document.getElementById('roomSelect');
    const mapTooltip = document.getElementById('mapTooltip');
    const tooltipName = document.getElementById('tooltipName');
    const tooltipDesc = document.getElementById('tooltipDesc');
    const stepsContainer = document.getElementById('stepsContainer');
    const routeSummary = document.getElementById('routeSummary');
    const accessibleToggle = document.getElementById('accessibleToggle');
    const serialLog = document.getElementById('serialLog');
    const activeDestinationText = document.getElementById('activeDestinationText');

    let currentSelectedRoomId = 2; // Default AQ 3150

    function initDropdown() {
      roomSelect.innerHTML = '';
      nodes.filter(n => n.id !== 0).forEach(node => {
        const option = document.createElement('option');
        option.value = node.id;
        option.textContent = `${node.name} (${node.level} Lvl)`;
        if (node.id === currentSelectedRoomId) option.selected = true;
        roomSelect.appendChild(option);
      });
    }

    function renderStaticMap() {
      edgesLayer.innerHTML = '';
      nodesLayer.innerHTML = '';

      edges.forEach(([u, v, dist, isStairs]) => {
        const nodeA = nodes.find(n => n.id === u);
        const nodeB = nodes.find(n => n.id === v);

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', nodeA.x);
        line.setAttribute('y1', nodeA.y);
        line.setAttribute('x2', nodeB.x);
        line.setAttribute('y2', nodeB.y);
        line.setAttribute('stroke', isStairs ? '#F59E0B' : '#334155');
        if (isStairs) line.setAttribute('stroke-dasharray', '5,5');
        edgesLayer.appendChild(line);
      });

      nodes.forEach(node => {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', 'cursor-pointer group');
        
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        
        let radius = 10;
        let fillColor = '#1E293B';
        let strokeColor = '#64748B';

        if (node.type === 'kiosk') {
          radius = 14;
          fillColor = '#10B981';
          strokeColor = '#059669';
        } else if (node.type === 'elevator') {
          fillColor = '#3B82F6';
          strokeColor = '#1D4ED8';
        } else if (node.type === 'stairs') {
          fillColor = '#F59E0B';
          strokeColor = '#D97706';
        }

        circle.setAttribute('r', radius);
        circle.setAttribute('fill', fillColor);
        circle.setAttribute('stroke', strokeColor);
        circle.setAttribute('stroke-width', '3');

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + (node.y > 300 ? 25 : -18));
        text.setAttribute('fill', node.type === 'kiosk' ? '#34D399' : '#94A3B8');
        text.setAttribute('font-size', '11');
        text.setAttribute('font-weight', node.type === 'kiosk' ? 'bold' : 'normal');
        text.setAttribute('text-anchor', 'middle');
        text.textContent = node.name.split('/')[0];

        group.appendChild(circle);
        group.appendChild(text);

        group.addEventListener('mouseenter', () => {
          tooltipName.textContent = node.name;
          tooltipDesc.textContent = `${node.desc} • Level ${node.level}`;
          mapTooltip.classList.remove('hidden');
        });

        group.addEventListener('mousemove', (e) => {
          const rect = svgMap.getBoundingClientRect();
          mapTooltip.style.left = `${e.clientX - rect.left + 15}px`;
          mapTooltip.style.top = `${e.clientY - rect.top - 15}px`;
        });

        group.addEventListener('mouseleave', () => {
          mapTooltip.classList.add('hidden');
        });

        if (node.id !== 0) {
          group.addEventListener('click', () => {
            currentSelectedRoomId = node.id;
            roomSelect.value = node.id;
            triggerRouteCalculation();
          });
        }

        nodesLayer.appendChild(group);
      });
    }

    function drawActivePath(pathNodes) {
      activePathLayer.innerHTML = '';
      if (!pathNodes || pathNodes.length < 2) return;

      for (let i = 0; i < pathNodes.length - 1; i++) {
        const u = nodes.find(n => n.id === pathNodes[i]);
        const v = nodes.find(n => n.id === pathNodes[i+1]);

        const pathLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        pathLine.setAttribute('x1', u.x);
        pathLine.setAttribute('y1', u.y);
        pathLine.setAttribute('x2', v.x);
        pathLine.setAttribute('y2', v.y);
        pathLine.setAttribute('stroke', '#A6192E');
        pathLine.setAttribute('stroke-width', '7');
        pathLine.setAttribute('stroke-linecap', 'round');
        pathLine.setAttribute('class', 'path-glow');
        pathLine.setAttribute('marker-end', 'url(#arrow)');

        activePathLayer.appendChild(pathLine);
      }
    }

    function triggerRouteCalculation() {
      const targetId = parseInt(roomSelect.value, 10);
      const isAccessible = accessibleToggle.checked;
      
      const { pathNodes, stepInstructions, totalDistance } = calculateShortestPath(0, targetId, isAccessible);

      drawActivePath(pathNodes);
      renderStepInstructions(stepInstructions, totalDistance);

      const targetNode = nodes.find(n => n.id === targetId);
      const payload = {
        status: "OK",
        kiosk_id: "AQ_3000_MAIN",
        target_room: targetNode ? targetNode.name : "Unknown",
        accessible_mode: isAccessible,
        total_distance_m: totalDistance,
        path_nodes: pathNodes,
        steps_count: stepInstructions.length
      };

      serialLog.textContent = `> SERIAL DATA OUT:\n` + JSON.stringify(payload, null, 2);
      activeDestinationText.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-400"></i> Route to <strong class="text-white">${targetNode ? targetNode.name : ''}</strong> active.`;
    }

    function renderStepInstructions(instructions, totalDist) {
      stepsContainer.innerHTML = '';

      if (instructions.length === 0) {
        stepsContainer.innerHTML = `<div class="p-4 text-center text-rose-400">No accessible path available.</div>`;
        return;
      }

      const approxWalkTimeMinutes = Math.max(1, Math.ceil(totalDist / 70));
      routeSummary.textContent = `${instructions.length} steps • ${totalDist}m (~${approxWalkTimeMinutes} min walk)`;

      instructions.forEach((step, idx) => {
        const stepCard = document.createElement('div');
        stepCard.className = `p-3.5 rounded-xl border transition-all ${idx === 0 ? 'bg-sfu-red/10 border-sfu-red/40' : 'bg-slate-900/60 border-dark-border hover:border-slate-700'}`;

        let icon = 'fa-solid fa-arrow-right text-sfu-red';
        if (step.isStairs) icon = 'fa-solid fa-stairs text-amber-400';
        if (step.text.includes('ELEVATOR')) icon = 'fa-solid fa-elevator text-blue-400';

        stepCard.innerHTML = `
          <div class="flex items-start gap-3">
            <div class="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-mono font-bold text-slate-300 flex-shrink-0 mt-0.5">
              ${idx + 1}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-semibold text-slate-200 flex items-center gap-2">
                <i class="${icon}"></i> ${step.text}
              </div>
              <div class="flex items-center justify-between text-[11px] text-slate-400 mt-1">
                <span>Toward: ${step.targetNodeName}</span>
                <span class="font-mono text-slate-500">${step.dist}m</span>
              </div>
            </div>
          </div>
        `;
        stepsContainer.appendChild(stepCard);
      });
    }

    /* =========================================================================
       4. HARDWARE SIMULATOR & WEB SERIAL API USB LINK
       ========================================================================= */
    const simPrevBtn = document.getElementById('simPrevBtn');
    const simNextBtn = document.getElementById('simNextBtn');
    const simSelectBtn = document.getElementById('simSelectBtn');
    const toggleHardwareBtn = document.getElementById('toggleHardwareBtn');
    const hardwarePanel = document.getElementById('hardwarePanel');
    const hwChevron = document.getElementById('hwChevron');
    const webSerialConnectBtn = document.getElementById('webSerialConnectBtn');

    simNextBtn.addEventListener('click', () => {
      let nextIdx = roomSelect.selectedIndex + 1;
      if (nextIdx >= roomSelect.options.length) nextIdx = 0;
      roomSelect.selectedIndex = nextIdx;
      triggerRouteCalculation();
    });

    simPrevBtn.addEventListener('click', () => {
      let prevIdx = roomSelect.selectedIndex - 1;
      if (prevIdx < 0) prevIdx = roomSelect.options.length - 1;
      roomSelect.selectedIndex = prevIdx;
      triggerRouteCalculation();
    });

    simSelectBtn.addEventListener('click', triggerRouteCalculation);

    accessibleToggle.addEventListener('change', () => {
      document.getElementById('accStatus').textContent = accessibleToggle.checked ? 'Accessible Only' : 'Standard Route';
      triggerRouteCalculation();
    });

    document.getElementById('calcRouteBtn').addEventListener('click', triggerRouteCalculation);
    roomSelect.addEventListener('change', triggerRouteCalculation);

    toggleHardwareBtn.addEventListener('click', () => {
      hardwarePanel.classList.toggle('hidden');
      hwChevron.classList.toggle('fa-chevron-down');
      hwChevron.classList.toggle('fa-chevron-up');
    });

    // Native Web Serial USB Link for Arduino
    if ("serial" in navigator) {
      webSerialConnectBtn.addEventListener('click', async () => {
        try {
          const port = await navigator.serial.requestPort();
          await port.open({ baudRate: 9600 });
          document.getElementById('hardwareStatus').textContent = "USB ARDUINO ONLINE";
          document.getElementById('hardwareStatus').className = "font-mono text-emerald-400 font-bold animate-pulse";
          
          const textDecoder = new TextDecoderStream();
          port.readable.pipeTo(textDecoder.writable);
          const reader = textDecoder.readable.getReader();

          while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            if (value) {
              serialLog.textContent = `> USB IN: ${value}\n` + serialLog.textContent;
            }
          }
        } catch (err) {
          console.error("Web Serial Error:", err);
        }
      });
    } else {
      webSerialConnectBtn.title = "Web Serial API not supported in this browser version. Use Simulation buttons.";
    }

    /* =========================================================================
       5. INITIALIZATION ON PAGE LOAD
       ========================================================================= */
    window.addEventListener('DOMContentLoaded', () => {
      initDropdown();
      renderStaticMap();
      triggerRouteCalculation();
    });
  </script>
</body>
</html>
