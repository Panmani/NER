import sys, os, subprocess
from .parse_script import *

NER_dir = ""
RE_dir = ""
PIPELINE_PARTS = [True, True, True] # Whether to run a part of the pipeline: [NER, DEP_PARSE, RE]

def extract(input_dir):
    input_files = os.listdir(input_dir)
    package_path, package_init = os.path.split(__file__)
    print(package_path)

    input_ids = []
    for input_file in input_files:
        if input_file[-3:] == "txt":
            input_ids.append(input_file[:-4])

    # ============================== Name Entity Recognition ==============================
    if PIPELINE_PARTS[0]:
        ner_path = os.path.join(package_path, NER_dir)
        # os.chdir(ner_path)
        for id in input_ids:
            txt_path = os.path.join(input_dir, id + ".txt")
            ner_script_path = os.path.join(package_path, "ner.py")
            subprocess.Popen(["python", ner_script_path, txt_path])

    # ============================== Dependency Parsing ==============================
    if PIPELINE_PARTS[1]:
        python_bin = os.path.join(package_path, RE_dir, "jPTDP-master/.DyNet/bin/python")
        script_file = os.path.join(package_path, RE_dir, "jPTDP-master/jPTDP.py")
        converter_file = os.path.join(package_path, RE_dir, "jPTDP-master/utils/converter.py")
        jPTDP_model_path = os.path.join(package_path, RE_dir, "jPTDP-master/sample/model256")
        jPTDP_params_path = os.path.join(package_path, RE_dir, "jPTDP-master/sample/model256.params")

        for id in input_ids:
            line_count = 0
            with open(os.path.join(input_dir, id + ".txt"), 'r') as input_file:
                os.system("mkdir " + os.path.join(input_dir, id))
                for line in input_file:
                    line_strip = clean_str(line.strip())
                    if line_strip != "" and not line_strip.isspace():
                        line_path = os.path.join(input_dir, id, str(line_count) + ".txt")
                        with open(line_path, 'w') as line_file:
                            line_file.write(line_strip)

                        parse_input = os.path.join(input_dir, id, str(line_count) + ".txt.conllu")
                        parse_output = parse_input + ".pred"

                        subprocess.Popen([python_bin, converter_file, line_path])
                        subprocess.Popen([python_bin, script_file, "--predict", \
                            "--model", jPTDP_model_path, "--params", jPTDP_params_path, \
                            "--test", parse_input, "--outdir", input_dir, "--output", parse_output])

                        line_count += 1

    if PIPELINE_PARTS[2]:
        # os.chdir(os.path.join(package_path, RE_dir, "2. dep"))
        for id in input_ids:
            parse_dir = os.path.join(input_dir, id)
            subprocess.Popen(["cp", parse_dir + ".ann", parse_dir + ".ann.sdp"])
            subprocess.Popen(["python", os.path.join(package_path, "relation_dep.py"), parse_dir, parse_dir + ".txt", parse_dir + ".ann.sdp"])


        # os.chdir(os.path.join(package_path, RE_dir, "3. nn"))
        for id in input_ids:
            parse_dir = os.path.join(input_dir, id)
            subprocess.Popen(["cp", parse_dir + ".ann", parse_dir + ".ann.nn"])
        subprocess.Popen(["python", os.path.join(package_path, "relation_nn.py"), input_dir])
