"""Curve interpolation must not draw gains outside the stored EQ bands."""
import shutil
import subprocess
import unittest
from pathlib import Path


class EqCurveMathTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is needed for pure UI math")
    def test_snapping_endpoints_and_monotone_segments_stay_in_band_range(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(["node", "-e", r'''
const assert = require("node:assert/strict");
const curve = require("./EqCurve.js");
assert.equal(curve.clampGain(12,-6,6,1),6);
assert.equal(curve.clampGain(-20,-6,6,1),-6);
assert.equal(curve.clampGain(2.7,-6,6,1),3);
assert.equal(curve.clampGain(-2.7,-6,6,1),-3);
for (const gains of [[4,1,-1,2,4,6],[-5,0,-6,0,0,0],[6,-6,6,-6,6,-6]]) {
  const p = curve.points(gains,250,120,-6,6);
  assert.equal(p[0].x,0); assert.equal(p[5].x,250);
  assert.equal(p[0].y,(6-gains[0])*10);
  const segments = curve.segments(p);
  assert.equal(segments.length,5);
  for (let i=0;i<5;i++) {
    const s=segments[i], a=p[i], b=p[i+1];
    let previous=a.y;
    for(let step=1;step<=20;step++) {
      let t=step/20,u=1-t;
      const y=u*u*u*a.y+3*u*u*t*s.c1.y+3*u*t*t*s.c2.y+t*t*t*b.y;
      assert(y>=Math.min(a.y,b.y)-1e-8 && y<=Math.max(a.y,b.y)+1e-8);
      assert((b.y>=a.y && y>=previous-1e-8)||(b.y<=a.y && y<=previous+1e-8));
      previous=y;
    }
  }
}
assert.deepEqual(curve.points([],250,120,-6,6),[]);
assert.equal(curve.points([0],250,120,-6,6)[0].x,125);
'''], cwd=root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
