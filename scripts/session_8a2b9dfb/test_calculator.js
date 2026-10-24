/* Synthetic-input regression tests for the actual browser calculator script.
   No retailer prices or measured weights are supplied by these test fixtures. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "../../assets/app.js"), "utf8");
const outputs = ["c-pure", "c-value", "c-min", "c-pergram", "c-mult"];
let passed = 0;
function test(name, fn) {
  fn();
  passed++;
  console.log("PASS: " + name);
}
function calculator(changes = {}, omitPrice = false) {
  const elements = {};
  // Defined troy-ounce conversion makes this SYNTHETIC rate exactly $100/g.
  const values = {"c-weight":"4", "c-karat":"18", "c-spot":"3110.34768", "c-price":"600", ...changes};
  for (const [id, value] of Object.entries(values)) {
    if (omitPrice && id === "c-price") continue;
    elements[id] = {value, addEventListener(type, callback) {this[type] = callback;}};
  }
  for (const id of [...outputs, "c-multnote"]) elements[id] = {textContent:""};
  vm.runInNewContext(source, {document: {
    getElementById: id => elements[id] || null,
    querySelectorAll: () => []
  }});
  return elements;
}
function blank(elements) {
  for (const id of outputs) assert.equal(elements[id].textContent, "—", id);
}

test("normal synthetic arithmetic and exact supported karat", () => {
  const el = calculator();
  assert.equal(el["c-pure"].textContent, "3.000 g");
  assert.equal(el["c-value"].textContent, "$300.00");
  assert.equal(el["c-min"].textContent, "$297.20");
  assert.equal(el["c-pergram"].textContent, "$100.00");
  assert.equal(el["c-mult"].textContent, "2.00×");
});
test("invalid, signed, nonfinite and partly numeric weights are not coerced", () => {
  for (const value of ["", "0", "-4", "NaN", "Infinity", "4 grams", "$4", "0x10", "1,000", "."])
    blank(calculator({"c-weight":value}));
});
test("missing or invalid spot is never inferred", () => {
  for (const value of ["", "0", "-100", "NaN", "Infinity", "100 USD"])
    blank(calculator({"c-spot":value}));
});
test("fractional/unsupported karats are not truncated to another purity", () => {
  for (const value of ["14.5", "14K", "99", "", "__proto__"])
    blank(calculator({"c-karat":value}));
});
test("finite input with overflowing derived gold value fails closed", () => {
  const el = calculator({"c-weight":"1e308"});
  blank(el);
  assert.match(el["c-multnote"].textContent, /safe numeric range/);
});
test("intermediate underflow does not produce phantom zero gold value", () => {
  blank(calculator({"c-weight":"1e-320", "c-spot":"1e-320"}));
});
test("ratio overflow does not display infinity or a false zero multiple", () => {
  const el = calculator({"c-weight":"1e-300", "c-price":"1e308"});
  assert.equal(el["c-mult"].textContent, "—");
  assert.doesNotMatch(el["c-mult"].textContent, /Infinity|∞|NaN|0\.00/);
});
test("optional price is not required for gold-content arithmetic", () => {
  const el = calculator({}, true);
  assert.equal(el["c-value"].textContent, "$300.00");
  assert.equal(el["c-mult"].textContent, "—");
});
test("input events clear an earlier valid result after invalidation", () => {
  const el = calculator();
  el["c-weight"].value = "not a weight";
  el["c-weight"].input();
  blank(el);
});
test("scientific decimal notation works when all results remain finite", () => {
  const el = calculator({"c-weight":"4e0"});
  assert.equal(el["c-value"].textContent, "$300.00");
});
console.log(`${passed} calculator runtime tests passed. Fixtures are hypothetical arithmetic, not sourced offers.`);
