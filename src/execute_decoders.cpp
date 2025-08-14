#include "instance/mcp_instance.hpp"
#include "brkga_mp_ipr.hpp"
#include "brkga_mp_ipr/chromosome.hpp"
#include "execute_decoders.hpp"
#include "decoders/coloracao3.hpp"
#include "decoders/coloracao3Corte.hpp"
#include "write_file.hpp"

#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <vector>
#include <queue>
#include <filesystem>

#define DEBUG 0
#define PRINT 0

using namespace std;

//-------------------------------[ Decoder execution - Coloração 3]------------------------------------//

void execute_coloracao3(
    const unsigned seed,
    const string config_file,
    const unsigned max_run_time,
    const string instance_file,
    const string output_file_name,
    const unsigned num_threads, const double B,const double epsilon, const std::string tipo_penalidade)
{
    try
    {
        cout << "Executing Decoder <coloracao3>" << endl;

        ////////////////////////////////////////
        // Read the instance
        ////////////////////////////////////////

        cout << "Reading data..." << endl;

        auto instance = MCP_Instance(instance_file);

        ////////////////////////////////////////
        // Read algorithm parameters
        ////////////////////////////////////////

        cout << "Reading parameters..." << endl;

        auto [brkga_params, control_params] = BRKGA::readConfiguration(config_file);

        // Overwrite the maximum time from the config file.
        control_params.maximum_running_time = chrono::seconds{max_run_time};

        ////////////////////////////////////////
        // Build the BRKGA data structures
        ////////////////////////////////////////

        cout << "Building BRKGA data and initializing..." << endl;

        MCP_Decoder_Coloracao3 decoder(instance, tipo_penalidade, B, epsilon);

        if(DEBUG > 2){
            instance.show();
            for(int i = 0; i < instance.num_edges * 2; i++){
                cout << decoder.position_edge_vector[i] << " ";
            }
            cout << endl;
        }


        unsigned chromossome_size = instance.num_nodes;

        BRKGA::BRKGA_MP_IPR<MCP_Decoder_Coloracao3> algorithm(
            decoder, BRKGA::Sense::MINIMIZE, seed,
            chromossome_size, brkga_params, num_threads);

        algorithm.reset(); // chama #initialize(true)

        // string instance_name = instance_file.substr(instance_file.length() - 9, 6);
        string instance_name = filesystem::path(instance_file).stem().string();

        /*

        // string caminho_arquivo_solucao_isolation = "../instances/concentric_sol/isolation_mcortes2/" + instance_name + ".sol";
        std::string caminho_arquivo_solucao_isolation = "/home/ricardo/Downloads/multiway/data2/basic_ih/" + instance_name + ".sol";


        // {
        algorithm.setInitialPopulation(
            vector<BRKGA::Chromosome>(1, gerador_cromossomo_col3(caminho_arquivo_solucao_isolation)));
        // }

        */

        ////////////////////////////////////////
        // Find good solutions / evolve
        ////////////////////////////////////////

        cout << "Running for " << control_params.maximum_running_time << "s..." << endl;

        const auto final_status = algorithm.run(control_params, &cout);

        /////////////////////////////////////////////////
        // Breadth-first search : encontrar o numero de nos na componente de cada terminal para o best_Cromossome
        /////////////////////////////////////////////////

        auto best_chromosome = final_status.best_chromosome;

        /// Armazena a cor de cada nó
        std::vector<int> color_node(instance.num_nodes, -1);

        /// Marcador de nós que originalmente podem ser visitados a partir de um terminal
        std::vector<bool> visited_node(instance.num_nodes, false);

        /// Determina a cor dos nós não-terminal
        for (unsigned u = 0; u < instance.num_nodes; u++)
        {
            color_node[u] = std::floor(best_chromosome[u] * instance.num_terminals);
        }

        /// Determina a cor de cada dos nós terminal
        for (unsigned i = 0; i < instance.num_terminals; i++)
        {
            unsigned s = instance.terminals[i];
            color_node[s] = i;
        }

        std::vector<unsigned> components_size;

        // realiza a marcação dos nós que originalmente podem ser visitados a partir de um terminal
        double naturally_cut_cost = decoder.bfs_visited_nodes(color_node, visited_node, components_size);

        // recolore nós isolados e calcula valor do corte
        double discount_cut_cost = decoder.bfs_recolor_nodes(color_node, visited_node, best_chromosome, components_size);

        if (DEBUG > 1)
        {
            cout << "Número de nós nas componentes do melhor cromossomo: " << endl;
            for (int i = 0; i < instance.num_terminals; i++)
            {
                cout << "num nós na componente do terminal " << i << " : " << components_size[i] << endl;
            }
            cout << endl;
        }

            
        vector<vector<unsigned>> componentes_solucao(instance.num_terminals,vector<unsigned>(0));


        //cout << "Nós em cada componente:" << endl;
        for(unsigned i = 0; i < instance.num_terminals; i++){
            unsigned s = instance.terminals[i];
            //cout << s << " = {";
            for(unsigned u = 0; u < instance.num_nodes; u++){
                if(color_node[u] == color_node[s]){
                    //cout << u << " ";
                    componentes_solucao[i].push_back(u);
                }
            }
            //cout <<"}" <<  endl;
        }


        /////////////////////////////////////////////////
        // Calcular penalidades possíveis (para o best chromosome)
        /////////////////////////////////////////////////



        bool is_valid;
        double penalidade;
        double fator_maxV_balPerfeito;
        
        if (tipo_penalidade == "maxzera")
        {
            penalidade = decoder.calc_penalidade_maxzera(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }else if(tipo_penalidade == "maxrange"){
            penalidade = decoder.calc_penalidade_maxrange(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }else if(tipo_penalidade == "quadzera"){
            penalidade = decoder.calc_penalidade_quadzera(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }else if(tipo_penalidade == "quadrange"){
            penalidade = decoder.calc_penalidade_quadrange(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }else if(tipo_penalidade == "quadrangetotal"){
            penalidade = decoder.calc_penalidade_quadrangetotal(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }else if(tipo_penalidade == "sem_penalidade"){
            penalidade = decoder.sem_penalidade(components_size, is_valid, fator_maxV_balPerfeito, B, epsilon);
        }

        /////////////////////////////////////////////////
        // Calcular apenas o custo do corte (para o best chromosome)
        /////////////////////////////////////////////////
        //double best_cost_corte = final_status.best_fitness / (1 + penalidade);

       
      cout
            //<< "\nDecoder original (com penalidade):\n"
            << "\nAlgorithm status: " << final_status;  // best_fitness do final_status é do decoder que consider penalidade
           //<< "\nNaturally cut cost : " << naturally_cut_cost
            //<< "\nDiscount cut cost:" << discount_cut_cost
            //<< endl;


        //cout << "\nDecoder Modificado (sem penalidade) \n";
        MCP_Decoder_Coloracao3Corte decoderC3(instance);
        BRKGA::fitness_t best_cost_corte = decoderC3.decode(best_chromosome, false);
        //cout << "\nBest Cost corte : " << best_cost_corte << "\n";


        vector<format_edge> edges_cuted;
        unsigned num_edges_cut = 0;

        write_in_file(
            output_file_name,
            instance.num_nodes,
            instance.num_edges,
            instance.num_terminals,
            is_valid, // valido se nenhuma parte tem mais que teto(b * (n.k)) nós
            best_cost_corte,
            final_status.last_update_iteration,
            final_status.last_update_time,
            final_status.current_iteration,
            final_status.current_time,
            num_edges_cut,
            edges_cuted,
            penalidade,
            fator_maxV_balPerfeito,
            componentes_solucao);
        
            write_parameters_in_file(output_file_name, B, epsilon, tipo_penalidade, seed);
    }
    catch (exception &e)
    {
        cerr
            << "\n"
            << string(40, '*') << "\n"
            << "Exception Occurred: " << e.what()
            << "\n"
            << string(40, '*')
            << endl;
    }
}