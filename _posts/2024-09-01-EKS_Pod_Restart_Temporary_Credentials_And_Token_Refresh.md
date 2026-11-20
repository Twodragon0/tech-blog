---
layout: post
title: "파드 재시작 시의 임시 자격 증명과 토큰 갱신"
date: 2024-09-01 20:36:28 +0900
last_modified_at: 2024-09-02T09:18:44+09:00
categories: [kubernetes, security]
tags: [EKS, IRSA, STS, IAM]
excerpt: "앞서 설명한 내용에서는 IRSA를 통해 파드가 AWS 리소스에 접근할 수 있는 임시 자격 증명을 어떻게 획득하고, 토큰이 만료되기 전에 어떻게 로테이션되는지를 설명했습니다. 이제, 파드가 재시작될 때 발생할 수 있는 상황과 이와 관련된 토큰 갱신 과정을 살펴보겠습니다."
description: "앞서 설명한 내용에서는 IRSA를 통해 파드가 AWS 리소스에 접근할 수 있는 임시 자격 증명을 어떻게 획득하고, 토큰이 만료되기 전에 어떻게 로테이션되는지를 설명했습니다. 이제, 파드가 재시작될 때 발생할 수 있는 상황과 이와 관련된 토큰 갱신 과정을 살펴보겠습니다."
keywords: [EKS, IRSA, STS, IAM]
author: Twodragon
comments: true
image: /assets/images/2024-09-01-EKS_Pod_Restart_Temporary_Credentials_And_Token_Refresh.jpg
image_alt: "EKS Pod Restart Temporary Credentials and Token Refresh"
toc: true
original_url: https://2twodragon.com/pod-restart-temp-auth-iam-role/
---

> 이 글은 2twodragon.com(워드프레스)에서 2024-09-01에 처음 게시된 글을 옮긴 것입니다.

앞서 설명한 내용에서는 IRSA를 통해 파드가 AWS 리소스에 접근할 수 있는 임시 자격 증명을 어떻게 획득하고, 토큰이 만료되기 전에 어떻게 로테이션되는지를 설명했습니다. 이제, 파드가 재시작될 때 발생할 수 있는 상황과 이와 관련된 토큰 갱신 과정을 살펴보겠습니다.

#### 파드 재시작 시의 상황

Kubernetes 환경에서 파드는 다양한 이유로 재시작될 수 있습니다. 예를 들어, 애플리케이션 업데이트, 장애 복구, 노드의 스케일링 또는 수동 재배포 등이 원인이 될 수 있습니다. 파드가 재시작되면 기존의 임시 자격 증명은 더 이상 유효하지 않으며, 새로운 자격 증명이 필요합니다.

#### 파드 재시작 시 임시 자격 증명 획득 과정

1.  **새로운 파드 생성:** 파드가 재시작되면 Kubernetes는 새로운 파드를 생성합니다. 이 과정에서 파드에 할당된 서비스 어카운트와 연결된 IAM 역할이 확인됩니다.
2.  **임시 자격 증명 요청:** 새로 생성된 파드는 kubelet을 통해 AWS IAM 역할과 연계된 새로운 임시 자격 증명을 요청합니다. 이 자격 증명은 새롭게 부여되며, 이전에 사용된 자격 증명은 더 이상 사용할 수 없습니다.
3.  **자격 증명의 주입:** 새로운 임시 자격 증명은 파드 내의 특정 경로에 주입됩니다. 파드는 이 자격 증명을 사용하여 AWS 리소스에 접근할 수 있게 됩니다.

#### 파드 재시작과 토큰 갱신의 중요성

파드가 재시작되면 새롭게 발급된 임시 자격 증명을 통해 AWS 리소스에 접근할 수 있기 때문에, 파드의 재시작은 자격 증명의 안전성을 보장하는 데 중요한 역할을 합니다. 즉, 임시 자격 증명이 유효하지 않거나 손상된 경우, 파드를 재시작함으로써 새로운 자격 증명을 확보할 수 있습니다.

#### 실무에서의 고려사항

파드가 재시작될 때마다 새로운 임시 자격 증명을 얻어야 한다는 점은 클라우드 인프라의 안정성과 보안을 높이는 데 기여하지만, 동시에 다음과 같은 사항들을 고려해야 합니다:

- **파드 초기화 시간:** 파드가 재시작되면서 새로운 자격 증명을 얻는 과정에서 약간의 지연이 발생할 수 있습니다. 이는 특히 높은 가용성을 요구하는 서비스에서 중요한 요소입니다.
- **애플리케이션의 유연성:** 애플리케이션이 새로운 자격 증명을 즉시 인식하고 사용할 수 있도록 구현되어야 합니다. 이는 재시작 시 자격 증명 로딩이 정상적으로 이루어지도록 설계되어야 합니다.
- **토큰 만료 처리:** 파드가 만료된 토큰을 사용하는 상황을 방지하기 위해, 애플리케이션은 주기적으로 토큰을 로드하고 이를 캐싱할 수 있는 메커니즘을 가져야 합니다.

### 파드 재시작 시 임시 자격 증명 갱신 알고리즘

아래는 파드 재시작 시 임시 자격 증명 갱신 과정을 표현한 알고리즘 다이어그램입니다:

```text
┌────────────────────────┐
│ 1. 파드 재시작 발생 │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 2. 새로운 파드 생성 │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 3. 파드에 할당된 │
│ 서비스 어카운트 확인│
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 4. kubelet이 AWS에 │
│ 임시 자격 증명 요청 │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 5. 새로운 임시 자격 증명 │
│ 발급 및 파드에 주입 │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 6. 파드는 임시 자격 증명 │
│ 사용해 AWS 리소스 접근 │
└────────────────────────┘
```

### 참고 자료

파드 재시작 시 임시 자격 증명 갱신과 관련된 더욱 자세한 내용은 아래 링크에서 확인할 수 있습니다:

- [Kubernetes에서 파드 라이프사이클 관리](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [AWS와 Kubernetes 통합: IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [Kubernetes에서의 서비스 어카운트 설정](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)

### 결론

파드 재시작 시 임시 자격 증명의 갱신과 새로운 자격 증명의 획득은 Kubernetes와 AWS 통합 환경에서 중요한 관리 요소입니다. 이를 통해 파드가 항상 유효한 자격 증명을 통해 안전하게 AWS 리소스에 접근할 수 있도록 보장할 수 있습니다. 실무에서는 이러한 과정이 원활하게 이루어지도록 파드 재시작 정책과 애플리케이션의 토큰 관리 방식을 신중하게 고려해야 합니다.

이러한 이해를 통해, 보다 안전하고 안정적인 클라우드 환경을 구축할 수 있을 것입니다.

### Renewal of Temporary Credentials and Token Rotation upon Pod Restart

In the previous sections, we discussed how IRSA enables a pod to access AWS resources by acquiring temporary credentials, and how token rotation occurs before expiration. Now, let’s delve into what happens when a pod restarts and how the related token renewal process is managed.

#### Scenario: Pod Restart

In a Kubernetes environment, pods can restart for various reasons, such as application updates, failure recovery, node scaling, or manual redeployment. When a pod restarts, the existing temporary credentials are no longer valid, and new credentials need to be obtained.

#### Process of Acquiring Temporary Credentials upon Pod Restart

1.  **Creation of a New Pod:** When a pod restarts, Kubernetes creates a new pod. During this process, the service account assigned to the pod and the associated IAM role are verified.
2.  **Request for Temporary Credentials:** The newly created pod requests new temporary credentials through the kubelet, which are linked to the associated AWS IAM role. The previous credentials are no longer usable.
3.  **Injection of Credentials:** The new temporary credentials are injected into the pod at a specific path, allowing the pod to access AWS resources securely.

#### Importance of Token Renewal and Pod Restart

When a pod restarts, it receives newly issued temporary credentials, ensuring continued secure access to AWS resources. Restarting the pod plays a critical role in maintaining the security of the credentials. If the temporary credentials are no longer valid or have been compromised, restarting the pod ensures that new credentials are acquired.

#### Considerations in Practice

While acquiring new temporary credentials upon each pod restart enhances cloud infrastructure security and stability, there are several practical considerations:

- **Pod Initialization Time:** There may be a slight delay when obtaining new credentials during pod initialization, which is especially important for services requiring high availability.
- **Application Flexibility:** The application should be designed to immediately recognize and use the new credentials. Properly handling credential loading during restarts is crucial.
- **Handling Token Expiration:** To prevent the pod from using expired tokens, the application should periodically reload tokens and implement a caching mechanism.

### Algorithm for Temporary Credentials Renewal upon Pod Restart

Below is an algorithm diagram representing the process of renewing temporary credentials upon pod restart:

```text
┌────────────────────────┐
│ 1. Pod Restarts │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 2. New Pod is Created │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 3. Verify Service │
│ Account Assigned to │
│ Pod │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 4. Kubelet Requests │
│ Temporary │
│ Credentials from AWS│
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 5. New Temporary │
│ Credentials Issued │
│ and Injected into │
│ Pod │
└──────────┬───────────┘
│
▼
┌────────────────────────┐
│ 6. Pod Uses Temporary │
│ Credentials to │
│ Access AWS Resources│
└────────────────────────┘
```

### References

For more detailed information on the renewal of temporary credentials upon pod restart, refer to the following links:

- [Managing Pod Lifecycle in Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Integrating AWS and Kubernetes: IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [Configuring Service Accounts in Kubernetes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)

### Conclusion

Renewing temporary credentials and acquiring new credentials upon pod restart are critical management aspects in a Kubernetes and AWS integrated environment. This process ensures that pods can always access AWS resources securely with valid credentials. In practice, careful consideration of pod restart policies and application token management is essential for smooth operations.

With this understanding, you can build a more secure and stable cloud environment.
