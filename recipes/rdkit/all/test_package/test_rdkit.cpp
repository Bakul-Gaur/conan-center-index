#include <GraphMol/FileParsers/FileParsers.h>
#include <GraphMol/GraphMol.h>
#include <GraphMol/SmilesParse/SmilesParse.h>

#include <iostream>
#include <memory>

using namespace std;

int main(int argc, char **argv) {
  string smiles = "CC(C)CC1=CC=CC=C1";

  shared_ptr<RDKit::ROMol> mol(RDKit::SmilesToMol(smiles));
  string molBlock = RDKit::MolToMolBlock(*mol);

  cout << molBlock << endl;

  return 0;
}
