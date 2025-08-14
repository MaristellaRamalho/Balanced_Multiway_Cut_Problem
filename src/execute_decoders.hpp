#ifndef EXECUTE_DECODERS_HPP_
#define EXECUTE_DECODERS_HPP_

#include <string>

void execute_coloracao3(
    const unsigned seed, const std::string config_file, 
    const unsigned max_run_time, const std::string instance_file, 
    std::string output_file_name, const unsigned num_threads, const double B, const double epsilon, const std::string tipo_penalidade
);


#endif