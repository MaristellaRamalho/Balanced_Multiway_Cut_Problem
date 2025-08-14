#include "execute_decoders.hpp"
#include "instance/mcp_instance.hpp"

#include <iostream>
#include <string>
#include <stdexcept>
#include <algorithm>

using namespace std;

// //-------------------------------[ Main ]------------------------------------//

int main(int argc, char* argv[])
{
    if(argc < 9) {
        cerr
        << "Usage: " << argv[0]
        << " <seed> <config-file> <maximum-running-time>"
        << " <mcp-instance-file> <decoder-name> <B> <epsilon> <tipo-penalidade> <output-file> "
        << endl;
        return 1;
    }

    try {
        ////////////////////////////////////////
        // Read command-line arguments and the instance
        ////////////////////////////////////////
        const unsigned seed = stoi(argv[1]);
        const string config_file = argv[2];
        const unsigned max_run_time = stoi(argv[3]);
        const string instance_file = argv[4];
        const string decoder_name = argv[5];
        const double B = stod(argv[6]);
        const double epsilon = stod(argv[7]);
        const string tipo_penalidade = argv[8];
        const string output_file_name = argv[9];
        const unsigned num_threads = 1;

        // MCP_Instance instance(instance_file);

        vector<string> penalidades = {"maxzera", "maxrange", "quadzera", "quadrange", "quadrangetotal", "sem_penalidade"};

        if(!(find(penalidades.begin(), penalidades.end(), tipo_penalidade) == penalidades.end())){// tipo_penalidade  está na lista
            if (decoder_name == "coloracao3") {
                execute_coloracao3(seed, config_file, max_run_time, instance_file, output_file_name, num_threads, B, epsilon, tipo_penalidade);
            }
            else {
                cerr
                << "Specified decoder not listed: "
                << "<coloracao3>"
                << endl;
            }
        }else{
            cerr
            << "Specified penalty not listed: "
            << "<maxzera> <maxrange> <quadzera> <quadrange> <quadrangetotal> <sem_penalidade>"
            << endl;
        }

    }
    catch(exception& e) {
        cerr
        << "\n" << string(40, '*') << "\n"
        << "Exception Occurred: " << e.what()
        << "\n" << string(40, '*')
        << endl;
        return 1;
    }

    return 0;
}
