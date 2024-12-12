import os
import shutil
import subprocess


##conda create -n annotation python=3.8
##conda activate annotation
##conda env config vars set GTDBTK_DATA_PATH="/mnt/f/binning/Annotation/release220" 手动设置参考数据位置
##验证是否成功安装：gtdbtk check_install

##python /mnt/f/binning/Annotation/annotation.py

# Utility function to run a shell command
def run_command(command, log_file):
    env = os.environ.copy()  # 获取当前环境变量
    with open(log_file, 'a') as log:
        log.write(f"Running command: {command}\n")
        print(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            log.write(f"Error running command: {command}\n")
            log.write(result.stderr + '\n')
            print(f"Error running command: {command}")
            print(result.stderr)
        log.write(result.stdout + '\n')
        print(result.stdout)
        return result.stdout

# Main execution
def main():
    log_file = "/mnt/f/binning/Annotation/annotation.log"
    input_dir = "/mnt/f/binning/Annotation/BK4"
    output_dir_gtdbtk = "/mnt/f/binning/Annotation/BK4/gtdbtk_output"
    output_dir_kofamscan = "/mnt/f/binning/Annotation/BK4/kofamscan_output"
    output_dir_phylophlan = "/mnt/f/binning/Annotation/BK1/phylophlan_output"
    prodigal_output_dir = "/mnt/f/binning/Annotation/BK1/prodigal_output"
    kofamscan_db_dir = "/mnt/f/binning/Annotation/kofamscan_db"
    
    # Set GTDBTK_DATA_PATH environment variable
    os.environ['GTDBTK_DATA_PATH'] = "/mnt/f/binning/Annotation/release220"
    print(f"GTDBTK_DATA_PATH is set to: {os.environ['GTDBTK_DATA_PATH']}")

    # 10.Run GTDB-Tk annotation for each .fna file
    for mag in os.listdir(input_dir):
        if mag.endswith(".fna"):
            mag_path = os.path.join(input_dir, mag)
            output_subdir = os.path.join(output_dir_gtdbtk, os.path.splitext(mag)[0])
            os.makedirs(output_subdir, exist_ok=True)
            #mash_db_path = "/mnt/f/binning/Annotation/mashdb"  # 你可以根据需要指定位置和名称,首次运行时需要，再次运行时用下面这个
            mash_db_path = "/mnt/f/binning/Annotation/mashdb.msh"
            run_command(f"gtdbtk classify_wf --genome_dir {input_dir} --out_dir {output_subdir} --cpus 16 --mash_db {mash_db_path} --scratch_dir /mnt/f/binning/Annotation/Temp", log_file)
            #run_command(f"gtdbtk classify_wf --genome_dir {input_dir} --out_dir {output_subdir} --cpus 2 --mash_db {mash_db_path}", log_file)
            # Run convert_to_itol
            #run_command(f"gtdbtk convert_to_itol --input {output_subdir}/classify/gtdbtk.bac120.classify.tree.2.tree --output {output_subdir}/itol_annotations.txt", log_file)
            
    # 11.Run KofamScan to assign K numbers for each .fna file
    os.makedirs(output_dir_kofamscan, exist_ok=True)
    os.makedirs(prodigal_output_dir, exist_ok=True)
    for mag in os.listdir(input_dir):
        if mag.endswith(".fna"):
            mag_path = os.path.join(input_dir, mag)
            protein_output_path = os.path.join(prodigal_output_dir, f"{os.path.splitext(mag)[0]}.faa")
            kofamscan_output_path = os.path.join(output_dir_kofamscan, f"{mag}.kofamscan.txt")
            
            # Run Prodigal to predict ORFs and generate protein sequences
            run_command(f"prodigal -i {mag_path} -a {protein_output_path} -m -p meta", log_file)
            
            # Run KofamScan to assign K numbers
            run_command(f"exec_annotation -f detail-tsv --cpu 16 -o {kofamscan_output_path} {protein_output_path} --ko-list {kofamscan_db_dir}/ko_list --profile {kofamscan_db_dir}/profiles", log_file)

    # 12.Run PhyloPhlAn for phylogenetic analysis
    # 生成默认配置文件用：phylophlan_write_default_configs.sh /mnt/f/binning/Annotation/phylophlan_configs
    # os.makedirs(output_dir_phylophlan, exist_ok=True)
    phylophlan_db_dir = "/mnt/f/binning/Annotation/phylophlan"
    input_dir_phylophlan = "/mnt/f/binning/Annotation/phylophlan/3bas"
    config_file = "/mnt/f/binning/Annotation/phylophlan_configs/supermatrix_aa.cfg"  # 或者其他你需要的配置文件
    # Use the "phylophlan" database, change to "3bas" if you prefer that
    database_name = "phylophlan"
    # run_command(f"phylophlan -i {input_dir_phylophlan} -o {output_dir_phylophlan} --databases {phylophlan_db_dir} -d {database_name} --nproc 16 --diversity high -f {config_file}", log_file)
    
    # 13.Run tvBOT for tree visualization
    input_tree = os.path.join(output_dir_phylophlan, "phylophlan_output.tree")
    output_dir_tvbot = os.path.join(output_dir_phylophlan, "tvbot_output")
    #os.makedirs(output_dir_tvbot, exist_ok=True)
    #run_command(f"tvbot {input_tree} -o {output_dir_tvbot}/tree_visualization.pdf", log_file)

if __name__ == "__main__":
    main()
