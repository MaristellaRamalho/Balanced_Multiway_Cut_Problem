#ifndef MCP_INSTANCE_HPP_
#define MCP_INSTANCE_HPP_

#include <string>
#include <vector>
#include <utility>

class MCP_Instance {
public:
    /// Number of nodes.
    unsigned num_nodes;

    /// Number of edges.
    unsigned num_edges;

    /// Number of terminals.
    unsigned num_terminals;

    /// Accumulated sum of edges cost.
    unsigned cumulative_edge_cost;

    /// Representation of edges (the source node is 
    /// represented by the adjacency list index where the arc e is).
    typedef struct {unsigned dst; unsigned cost;} edge;

    /// Graph in adjascency list representation.
    std::vector<std::vector<edge>> G;

    /// Terminal set S.
    std::vector<unsigned> terminals;

public:
    /// Default Constructor.
    MCP_Instance(const std::string& filename);

    // returns the position where the arc (i,j) is in the adjacency list of i
    // or returns -1 if the arc does not exist.
    int get_edge_index(unsigned u, unsigned v) const;

    /// Show graph
    void show() const;
};

#endif // MCP_INSTANCE_HPP_
