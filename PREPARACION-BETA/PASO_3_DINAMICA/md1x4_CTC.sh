#!/bin/bash

cp -r md1/ md2



#############################################################################
cd md2/

#rm md1.JobInfo
#rm output*
rm md1.sh # Borramos el lanzador del npt0.sh porque puede ser el del CTC o no. Así nos aseguramos de que funciona
rm md1_CTC.sh # Tampoco queremos el del CTC porque lo vamos a generar
rm md1.out
rm md1.rst
rm md1.mdcrd
rm md1.job.out
rm md1.info
rm md1.err


# Ahora generamos el lanzador adecuado para el CTC #

cat > md2_CTC.sh <<EOF
#!/bin/bash
#SBATCH --job-name=md2
#SBATCH --output=md2.job.out
#SBATCH --error=md2.err
#SBATCH --partition=gpusNodes
#SBATCH --gres=gpu:1
#SBATCH -n 2
#SBATCH -N 1
#SBATCH --mem=40G
# Variables de entorno para ajuste de paralelismo híbrido y afinidad
# (En GPU no tengo nada por ahora, pero se podría hacer "export CUDA_VISIBLE_DEVICES=0" si fuera necesario)
pmemd.cuda -O -i md1.in -o md2.out -p system_hmass.prmtop -c npt0.rst -r md2.rst -x md2.mdcrd -inf md2.info

EOF

cd ..



###########################################################################
###########################################################################
cp -r md2/ md3

cd md3/

mv md2_CTC.sh md3_CTC.sh

sed -i 's|^pmemd.cuda -O -i md1.in -o md2.out -p system_hmass.prmtop -c npt0.rst -r md2.rst -x md2.mdcrd -inf md2.info$|pmemd.cuda -O -i md1.in -o md3.out -p system_hmass.prmtop -c npt0.rst -r md3.rst -x md3.mdcrd -inf md3.info|;s|^#SBATCH --job-name=md2$|#SBATCH --job-name=md3|;s|^#SBATCH --output=md2.job.out$|#SBATCH --output=md3.job.out|;s|^#SBATCH --error=md2.err$|#SBATCH --error=md3.err|' md3_CTC.sh


cd ..
#############################################################################

cp -r md2/ md4

cd md4/

mv md2_CTC.sh md4_CTC.sh

sed -i 's|^pmemd.cuda -O -i md1.in -o md2.out -p system_hmass.prmtop -c npt0.rst -r md2.rst -x md2.mdcrd -inf md2.info$|pmemd.cuda -O -i md1.in -o md4.out -p system_hmass.prmtop -c npt0.rst -r md4.rst -x md4.mdcrd -inf md4.info|;s|^#SBATCH --job-name=md2$|#SBATCH --job-name=md4|;s|^#SBATCH --output=md2.job.out$|#SBATCH --output=md4.job.out|;s|^#SBATCH --error=md2.err$|#SBATCH --error=md4.err|' md4_CTC.sh


cd ..
###############################################################################


cd md2/ 
sbatch md2_CTC.sh
cd ..

cd md3/ 
sbatch md3_CTC.sh
cd ..

cd md4/ 
sbatch md4_CTC.sh
cd ..



