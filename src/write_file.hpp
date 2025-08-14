#ifndef WRITE_FILEeee_HPP_
#define WRITE_FILEeee_HPP_

#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>

using namespace std;

// Auxiliar edge structure
typedef struct { unsigned src; unsigned dst; unsigned cost; } format_edge;

void write_in_file (
    string file_name,
    unsigned num_nodes,
    unsigned num_edges,
    unsigned num_terminals,
    bool is_valid_solution,
    double best_fitness,
    long last_update_iteration,
    std::chrono::duration<double> last_update_time,
    long current_iteration,
    std::chrono::duration<double> current_time,
    unsigned num_edges_cuted,
    vector<format_edge>& edges_cuted,
    double penalidade,
    double fator_maxV_balPerfeito,
    vector<vector<unsigned>> &componentes_solucao
);

void write_parameters_in_file(string file_name, double B, double epsilon, string tipo_penalidade, const unsigned seed);

#endif