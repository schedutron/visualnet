// Random tree
const NODES = 300;
const GROUPS = 12;

const gData = spiderJsonFull;
const fxs = gData["nodes"].map(node => node.fx);
const fys = gData["nodes"].map(node => node.fy);
const fzs = gData["nodes"].map(node => node.fz);

const fxMin = Math.min(...fxs);
const fyMin = Math.min(...fys);
const fzMin = Math.min(...fzs);

const fxMax = Math.max(...fxs);
const fyMax = Math.max(...fys);
const fzMax = Math.max(...fzs);

const colorR = fxs.map(x => ((x-fxMin) / (fxMax-fxMin)) * 255);
const colorG = fys.map(y => ((y-fyMin) / (fyMax-fyMin)) * 255);
const colorB = fzs.map(z => ((z-fzMin) / (fzMax-fzMin)) * 255);


gData["nodes"] = gData["nodes"].map((node, idx) => ({
  id: node.id,
  url: node.url,
  old_rank: node.old_rank,
  new_rank: node.new_rank,
  val: node.new_rank,  // do relative sizing via rank / (max_rank+1)
  color: `rgba(${colorR[idx]}, ${colorG[idx]}, ${colorB[idx]}, 0.7)`,
  group: Math.ceil(Math.random() * GROUPS)
}));

gData["links"] = gData["links"].map(link => ({
  source: gData.nodes.find(node => node.id === link.source.id),
  target: gData.nodes.find(node => node.id === link.target.id),
  value: 3
}));

function updateHighlight() {
// trigger update of highlighted objects in scene
  Graph
  .nodeColor(Graph.nodeColor())
  .linkWidth(Graph.linkWidth())
  .linkDirectionalParticles(Graph.linkDirectionalParticles());
}

let highlightNodes = [];
let highlightLink = null;

const Graph = ForceGraph3D()
(document.getElementById('3d-graph'))
  .nodeVal('val')
  .linkColor(d => d.source.color)
  .nodeLabel('url')
  .linkDirectionalParticleWidth(1)
  .linkDirectionalParticles(d => 2)
  .linkDirectionalParticleSpeed(d => 0.003)
  .onNodeClick(node => {
    // Aim at node from outside it
    const distance = 40;
    const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
    Graph.cameraPosition(
      { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, // new position
      node, // lookAt ({ x, y, z })
      3000  // ms transition duration
    );
    window.open(node.url, '_blank');
  })
  .linkOpacity(0.5)
  .width(1000)
  .height(800)
  .graphData(gData);
