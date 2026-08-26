// Een Worker mag maar een beperkt aantal keer naar buiten per uitvoering
// (50 op het gratis plan, 1000 op het betaalde). Feed-detectie en deelnames
// tellen daarin allebei mee, dus houden we zelf bij hoeveel er nog over is.
// Zonder dit loopt de teller stiekem vol en mislukt alles wat daarna komt.

export class BudgetOp extends Error {
  constructor() {
    super("subrequest-budget op voor deze ronde");
    this.name = "BudgetOp";
  }
}

export const budget = {
  limiet: 45,
  gebruikt: 0,
  reset(limiet) {
    this.limiet = limiet;
    this.gebruikt = 0;
  },
  over() {
    return this.limiet - this.gebruikt;
  },
  neem() {
    if (this.gebruikt >= this.limiet) throw new BudgetOp();
    this.gebruikt += 1;
  },
};
