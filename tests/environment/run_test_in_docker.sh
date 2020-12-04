#!/usr/bin/env bash
PROJECT_REPO_NAME="u_shape_framework"

if [[ $1 ]];then
    output_report_path=$1
else
    output_report_path="../"
fi

python2_test_image="dockerhub.datagrand.com/nlp/${PROJECT_REPO_NAME}:python2_dev"
python2_test_container_name="${PROJECT_REPO_NAME}_dev_${RANDOM}"

sh build_python2_docker_dev.sh ${python2_test_image}

if [[ "$(docker ps -q ${python2_test_container_name} 2> /dev/null)" != "" ]]; then
    echo "container $python2_test_container_name exist, remove it"
    docker stop ${python2_test_container_name} && docker rm ${python2_test_container_name}
fi

echo "run test in container: $python2_test_container_name"
docker run -d --name ${python2_test_container_name} ${python2_test_image}
docker exec ${python2_test_container_name} bash -c "cd ./tests/environment && python run_all_test_cases.py"
python2_test_status=$?

docker cp ${python2_test_container_name}:/root/${PROJECT_REPO_NAME}/tests/TestReport.html ${output_report_path}/TestReport_python2.html
docker stop ${python2_test_container_name}
docker rm ${python2_test_container_name}

python3_test_image="dockerhub.datagrand.com/nlp/${PROJECT_REPO_NAME}:python3_dev"
python3_test_container_name="${PROJECT_REPO_NAME}_dev_${RANDOM}"

sh build_python3_docker_dev.sh ${python3_test_image}

if [[ "$(docker ps -q ${python3_test_container_name} 2> /dev/null)" != "" ]]; then
    echo "container $python3_test_container_name exist, remove it"
    docker stop ${python3_test_container_name} && docker rm ${python3_test_container_name}
fi

echo "run test in container: $python3_test_container_name"
docker run -d --name ${python3_test_container_name} ${python3_test_image}
docker exec ${python3_test_container_name} bash -c "cd ./tests/environment && python run_all_test_cases.py"
python3_test_status=$?

docker cp ${python3_test_container_name}:/root/${PROJECT_REPO_NAME}/tests/TestReport.html ${output_report_path}/TestReport_python3.html
docker stop ${python3_test_container_name}
docker rm ${python3_test_container_name}

if [[ ${python2_test_status} -ne 0 ]]; then
    echo "python2 test job fail"
    exit 1
fi
if [[ ${python3_test_status} -ne 0 ]]; then
    echo "python3 test job fail"
    exit 1
fi