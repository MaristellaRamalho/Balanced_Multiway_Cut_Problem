#ifndef MCP_DECODER_COLORACAO3_HPP_
#define MCP_DECODER_COLORACAO3_HPP_

#include "instance/mcp_instance.hpp"
#include "brkga_mp_ipr/fitness_type.hpp"
#include "brkga_mp_ipr/chromosome.hpp"


class MCP_Decoder_Coloracao3 {
public:
    /// Auxiliary edge structure
    typedef struct {unsigned src; unsigned dst; unsigned cost; unsigned edge_index; } edge;

    /// A reference to a MCP instance.
    const MCP_Instance& instance;

    /// Position of the beginning of the adjacency list of each node in vector
    std::vector<unsigned> init_adjacency_list;

    /// Position of each edge in the edge vector (mapping 2*m -> m)
    std::vector<unsigned> position_edge_vector;

    /// Tipo de penalidade
    const std::string tipo_penalidade;

    /// parâmetro B
    const double B;

    /// parâmetro epsilon
    const double epsilon;

public:
    /// Constructor and main function of the decoder

    MCP_Decoder_Coloracao3(const MCP_Instance& instance, const std::string tipo_penalidade, const double B, const double epsilon);

    BRKGA::fitness_t decode(BRKGA::Chromosome& chromosome, bool rewrite);

    /// Search edges in cut

    double bfs_visited_nodes(std::vector<int>& color_node, std::vector<bool>& visited_node, std::vector<unsigned>& components_size);

    double bfs_recolor_nodes(std::vector<int>& color_node, std::vector<bool>& visited_node, BRKGA::Chromosome& chromosome,  std::vector<unsigned>& components_size);

    unsigned get_edge_index(unsigned u, unsigned v);

    //Cálculos de penalidade 
    
    double calc_penalidade_maxzera(std::vector<unsigned>& components_size, bool& is_valid, double& fator_maxV_balPerfeito, const double B, const double epsilon); // considera penalidade zero para soluções em que nenhuma parte ultrapassa teto(b * (n/k)) para o número de nós -> penaliza apenas soluções inválidas

    double calc_penalidade_maxrange(std::vector<unsigned>& components_size, bool& is_valid, double& fator_maxV_balPerfeito, const double B, const double epsilon); // penaliza soluções inválidas e soluções válidas dentro da faixa [n/k , b(n/k)]

    double calc_penalidade_quadzera(std::vector<unsigned> &components_size, bool& is_valid, double& fator_maxV_balPerfeito,const double B, const double epsilon); // considera penalidade zero para soluções em que nenhuma parte ultrapassa teto(b * (n/k)) para o número de nós -> penaliza apenas soluções inválidas usando a ideia dos mínimos quadrados


    double calc_penalidade_quadrange(std::vector<unsigned> &components_size, bool& is_valid, double& fator_maxV_balPerfeito, const double B, const double epsilon); //penaliza soluções inválidas e componentes de soluções válidas cujo tamanho esta dentro da faixa [n/k , b(n/k)] usando a ideia de mínimos quadrados

    double calc_penalidade_quadrangetotal(std::vector<unsigned> &components_size, bool& is_valid, double& fator_maxV_balPerfeito, const double B, const double epsilon); //penaliza soluções inválidas e soluções válidas usando a ideia de mínimos quadrados

    double sem_penalidade(std::vector<unsigned> &components_size, bool& is_valid, double& fator_maxV_balPerfeito, const double B, const double epsilon); // retorna 0 -> decoder sem penalidade no processo evolutivo


};

#endif // MCP_DECODER_HPP_