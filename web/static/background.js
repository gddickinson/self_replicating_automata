// Background page: the theory and history from README_automata.md, and how each idea maps onto the class the code
// actually runs (the aliases at the bottom of self_replicating_automata.py).
import { route, app } from './core.js';

route('background', () => {
  app().innerHTML = `
  <p class="kicker">Background · from README_automata.md</p>
  <h1>Self-reproducing automata</h1>
  <p class="lead">The repository's README describes the ideas behind the simulator. This page repeats that background and
  says, for each idea, which class the code runs for it.</p>

  <h2>Von Neumann's original work (1940s-1950s)</h2>
  <p>Von Neumann's self-replicating automaton was designed to prove that machines could theoretically reproduce
  themselves. His system included:</p>
  <ul>
    <li><b>29 cell states</b> in a 2D cellular grid</li>
    <li><b>Universal constructor</b>: could build any pattern based on instructions</li>
    <li><b>Tape/memory</b>: stored the "genome" or construction instructions</li>
    <li><b>Copier</b>: duplicated the instructions for offspring</li>
  </ul>
  <h3>Key insight</h3>
  <p>Von Neumann solved the paradox "How can something create something as complex as itself?" with a two-fold approach:
  instructions used as <b>data</b> (interpreted to build the offspring) and as <b>passive information</b> (copied blindly
  to the offspring). This predates and parallels the discovery of DNA's dual role. His work arrived at concepts similar
  to self-description (genetic code), universal construction (ribosomes) and information duplication (replication).</p>

  <h2>The ideas and what this code runs</h2>
  <div class="scroll"><table>
    <thead><tr><th>Idea (README_automata.md)</th><th>What the README says</th><th>What the code runs</th></tr></thead>
    <tbody>
      <tr><td>Langton's self-replicating loop</td><td>A simplified version of von Neumann's idea using only 8 states: a closed
        loop that extends an "arm" to replicate. Published in 1984.</td>
        <td><a href="#/lab/langton_loop"><code>SimplifiedLangtonLoop</code></a>: 8 states (only 0-2 used), 12 hand-written rules generalised
        to every neighbour arrangement plus an arm-opening rule; the loop grows sheathed arms that branch, it does not copy
        itself (the ROADMAP lists "implement a true Langton Loop with the full 219-rule transition table" as future
        work).</td></tr>
      <tr><td>Evolving loop (evoloops)</td><td>Based on Sayama's 1999 work: loops that can undergo Darwinian evolution
        through mutation, selection and inheritable variation.</td>
        <td><a href="#/lab/brians_brain"><code>BriansBrain</code></a>, aliased as <code>EvolvingLoop</code> ("Use Brian's
        Brain as a working evolving pattern"); it has no mutation or loops.</td></tr>
      <tr><td>Von Neumann universal constructor</td><td>A simplified demonstration of universal construction: instruction
        tape, construction arm, signal propagation, pattern assembly.</td>
        <td><a href="#/lab/game_of_life"><code>GameOfLifeReplicator</code></a>, aliased as
        <code>VonNeumannConstructor</code> ("Use Life as constructor demo"): Conway's Life with Gosper's glider gun.</td></tr>
      <tr><td>Wire World</td><td>Not a replicator, but demonstrates signal propagation: electron-like signals moving through
        conductors, important for understanding how information flows in self-replicating systems.</td>
        <td><a href="#/lab/wireworld"><code>WireWorld</code></a>: the standard 4-state rule.</td></tr>
    </tbody></table></div>
  <div class="callout">From the README: "These are simplified demonstrations. von Neumann's original 29-state automaton is
  far more complex and truly universal - it can construct any pattern, including a complete copy of itself with arbitrary
  complexity."</div>

  <h2>Key concepts to observe</h2>
  <ol>
    <li><b>Self-description</b>: the system contains a description of itself</li>
    <li><b>Universal construction</b>: building arbitrary patterns from instructions</li>
    <li><b>Information duplication</b>: copying genetic information to offspring</li>
    <li><b>Emergence</b>: complex behaviour from simple rules</li>
    <li><b>Evolution</b>: variation and selection over generations</li>
  </ol>

  <h2>Current research directions (2024-2025)</h2>
  <ul>
    <li><b>Open-ended evolution</b>: systems that evolve indefinitely with increasing complexity</li>
    <li><b>Continuous cellular automata</b>: moving beyond discrete states</li>
    <li><b>Computational complexity</b>: the minimum complexity for self-reproduction</li>
    <li><b>Physical implementation</b>: nano-scale and molecular self-replicators</li>
  </ul>

  <h2>References</h2>
  <ul>
    <li>von Neumann, J. (1966). <i>Theory of Self-Reproducing Automata</i></li>
    <li>Langton, C. (1984). Self-reproduction in cellular automata</li>
    <li>Sayama, H. (1999). Introduction of structural dissolution into Langton's self-reproducing loop</li>
    <li>Sayama, H. &amp; Nehaniv, C.L. (2025). Self-Reproduction and Evolution in Cellular Automata: 25 Years After Evoloops</li>
  </ul>`;
});
