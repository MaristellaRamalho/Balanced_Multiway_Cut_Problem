#include "decoders/coloracao3Corte.hpp"

#include <iostream>
#include <algorithm>
#include <queue>
#include <vector>
#include <iomanip>
#include <cmath>

#define DEBUG 0
#define PRINT 0

using namespace std;
using namespace BRKGA;

// unsigned NUM_CROMOSOMO = 0;

/*
    O que mudou:

    Nessa terceira versão do decoder baseado em coloração de grafos, mantemos a busca em largura a partir de cada
    terminal s para identificar quais nós não-terminais da cor de s podem ser "naturalmente" visitados a partir
    dele e contabilizamos como arcos de fronteira, aqueles que ligam um nó visitado de cor x a um nó qualquer de cor y.

    Realizamos uma segunda busca a partir de cada nó não visitado (desconsidarando sua cor). Todo nó também não-visitado
    encontrado a partir dele desencadeia a continuação da busca. Para os arcos que ligam estes a nós que naturalmente
    foram visitados, contabilizamos o custo desses arcos separados por cor.
    No fim dessa segunda busca, temos, para cada cor, o custo da fronteira com essa componente desconexa. Atribuimos então
    à esses nós desconexos a cor com maior custo de fronteira e alteramos o cromossomo para refletir essa mudança de cor.

    Essa versão NÃO considera penalidade no processo evolutivo -> é exatamente o decoder original do Ricardo desenvolvido para o Multiway Cut Problem
*/

//-----------------------------[ Constructor ]--------------------------------//

MCP_Decoder_Coloracao3Corte::MCP_Decoder_Coloracao3Corte(const MCP_Instance &_instance) : instance(_instance),
                                                                                init_adjacency_list(instance.num_nodes, -1),
                                                                                position_edge_vector(instance.num_edges * 2, -1)
{
    unsigned list_position = 0;
    unsigned edge_position = 0;
    unsigned u, v;

    for (u = 0; u < instance.num_nodes; u++)
    {
        init_adjacency_list[u] = list_position;

        std::vector<MCP_Instance::edge> u_list = instance.G[u];

        for (unsigned i = 0; i < u_list.size(); i++)
        {
            v = u_list[i].dst;

            if (u < v)
            {
                position_edge_vector[list_position + i] = edge_position;
                edge_position++;
            }
            else
            { // A posição de (u,v) no vetor já foi determinada previamente a partir de (v,u)
                position_edge_vector[list_position + i] =
                    position_edge_vector[init_adjacency_list[v] + instance.get_edge_index(v, u)];
            }
        }

        list_position += u_list.size();
    }
}


//-------------------------------[ Decode ]-----------------------------------//

BRKGA::fitness_t MCP_Decoder_Coloracao3Corte::decode(Chromosome &chromosome, bool /* not-used */)
{
    // cout << NUM_CROMOSOMO << ": ";
    // for (auto x: chromosome)
    //     cout << x << " ";
    // cout << endl << endl;
    // NUM_CROMOSOMO++;

    /// Armazena a cor de cada nó
    std::vector<int> color_node(instance.num_nodes, -1);

    /// Marcador de nós que originalmente podem ser visitados a partir de um terminal
    std::vector<bool> visited_node(instance.num_nodes, false);

    /// Determina a cor dos nós não-terminal
    for (unsigned u = 0; u < instance.num_nodes; u++)
    {
        color_node[u] = std::floor(chromosome[u] * instance.num_terminals);
    }

    /// Determina a cor de cada dos nós terminal
    for (unsigned i = 0; i < instance.num_terminals; i++)
    {
        unsigned s = instance.terminals[i];
        color_node[s] = i;
        // TODO: atualizar cromossomo com a cor dos terminais também
    }

    std::vector<unsigned> components_size;

    // realiza a marcação dos nós que originalmente podem ser visitados a partir de um terminal
    double naturally_cut_cost = bfs_visited_nodes(color_node, visited_node, components_size);

    // recolore nós isolados e calcula valor do corte
    double discount_cut_cost = bfs_recolor_nodes(color_node, visited_node, chromosome, components_size);

    if (PRINT)
    {
        for (int i = 0; i < instance.num_terminals; i++)
        {
            cout << "num nós na componente do terminal " << i << " : " << components_size[i] << endl;
        }
        cout << endl;
    }

    bool is_valid;
    double fator_maxV_balPerfeito;
   

    double fit = (naturally_cut_cost - discount_cut_cost);
    //cout << "naturally_cut_cost : " << naturally_cut_cost << endl;
    //cout << "discount_cut_cost : " << discount_cut_cost << endl;
    //cout << "Fit : " << fit << endl;

    return fit;
}

//-----------------------------[ Calcula nós que podem ser visitados ]--------------------------------//

double MCP_Decoder_Coloracao3Corte::bfs_visited_nodes(
    std::vector<int> &color_node,
    std::vector<bool> &visited_node,
    std::vector<unsigned> &components_size)
{
    /// Armazena o custo acumulado dos cortes
    double cut_cost = 0;

    /// Fila que armazena os nós encontrados
    std::queue<unsigned> queue;

    /// Armazena o número de vezes que um arco apareceu na fronteira de um corte
    std::vector<unsigned> num_cuts_edge(instance.num_edges, 0);

    /////////////////////////////////////////////////
    // Breadth-first search para encontrar os nós de
    // mesma cor que são alcançáveis a partir de cada
    // terminal
    /////////////////////////////////////////////////

    unsigned edge_index = 0;
    unsigned terminal_index = 0;
    components_size.resize(instance.num_terminals, 0);

    for (unsigned s : instance.terminals)
    {

        visited_node[s] = true;
        queue.push(s);

        while (!queue.empty())
        {

            unsigned u = queue.front();
            queue.pop();
            components_size[terminal_index]++;

            /// Obtem a lista de arestas que saem de u
            const std::vector<MCP_Instance::edge> &u_list = instance.G[u];

            for (unsigned i = 0; i < u_list.size(); i++)
            {
                unsigned v = u_list[i].dst;

                if (color_node[v] == color_node[u])
                {
                    if (visited_node[v] == false)
                    {
                        visited_node[v] = true;
                        queue.push(v);
                    }
                }
                else
                {
                    /// Calcula o índice do arco no vetor
                    edge_index = position_edge_vector[init_adjacency_list[u] + i];

                    /// Incrementa o número de fronteiras que o arco foi encontrado
                    num_cuts_edge[edge_index]++;

                    /// Considera o custo deste arco apenas uma vez
                    if (num_cuts_edge[edge_index] == 1)
                    {
                        cut_cost += u_list[i].cost;
                    }
                }
            }
        }
        terminal_index++;
    }

    return cut_cost;
}

//-----------------------------[ Recolore nós ]--------------------------------//

double MCP_Decoder_Coloracao3Corte::bfs_recolor_nodes(
    std::vector<int> &color_node,
    std::vector<bool> &naturally_visited_node,
    BRKGA::Chromosome &chromosome,
    std::vector<unsigned> &components_size)
{
    /// Armazena o custo acumulado das arestas que foram removidas de fronteiras de cortes
    double discount_edges_cost = 0;

    /// Fila  que armazena os nós encontrados
    std::queue<unsigned> queue;

    ///
    std::vector<bool> visited_node(instance.num_nodes, false);

    /////////////////////////////////////////////////
    // Breadth-first search para encontrar e recolorir
    // nós que não puderam ser originalmente visitados
    /////////////////////////////////////////////////

    for (unsigned w = 0; w < instance.num_nodes; w++)
    {

        if (naturally_visited_node[w] == false and visited_node[w] == false)
        {

            visited_node[w] = true;
            queue.push(w);

            /// Armazena o custo das arestas na fronteira da componente formada
            /// por essa busca separado por cada cor encontrada
            std::vector<unsigned> cost_edges_border_by_color(instance.num_terminals, 0);

            /// Armazena o rótulo dos nós que não foram "naturalmente" visitados para posterior recoloração
            std::vector<unsigned> nodes_to_recolor;

            while (!queue.empty())
            {

                /// Remove o primeiro nó da fila de encontrados
                unsigned u = queue.front();
                queue.pop();

                /// Insere u na lista de recoloração
                nodes_to_recolor.push_back(u);

                /// Obtém a lista de arestas que saem de u
                const std::vector<MCP_Instance::edge> &u_list = instance.G[u];

                for (unsigned i = 0; i < u_list.size(); i++)
                {

                    unsigned v = u_list[i].dst;
                    unsigned cost = u_list[i].cost;

                    if (naturally_visited_node[v] == false)
                    {
                        if (visited_node[v] == false)
                        {
                            visited_node[v] = true;
                            queue.push(v);
                        }
                        // else
                        // v já foi visitado nessa busca
                    }
                    else
                    {
                        cost_edges_border_by_color[color_node[v]] += cost;
                    }
                }
            }

            double best_border_cost = 0;
            double best_border_color = -1;

            for (unsigned color = 0; color < instance.num_terminals; color++)
            {
                if (cost_edges_border_by_color[color] > best_border_cost)
                {
                    best_border_cost = cost_edges_border_by_color[color];
                    best_border_color = color;
                }
            }

            // Encontra para a componente de qual terminal as componentes isoladas foram atribuídas
            components_size[best_border_color] += nodes_to_recolor.size();

            discount_edges_cost += best_border_cost;

            if (best_border_cost > 0)
            {
                for (unsigned u : nodes_to_recolor)
                {
                    // Altera a cor do nó u
                    color_node[u] = best_border_color;

                    // Converte o alelo do nó u no cromossomo
                    chromosome[u] = ((double)color_node[u] / (double)instance.num_terminals) + ((double)1 / (2 * instance.num_terminals));

                    // TODO: marcar ele como naturally visited também
                }
            }
        }
    }

    return discount_edges_cost;
}