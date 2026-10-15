"""Build the TRISHA ACADEMY Kubernetes course: one combined book plus one PDF per class (11 classes).

Run:  python generate_k8s_course_pdf.py
Output goes to docs/kubernetes/.
"""
import os

from k8s_pdf_lib import draw_cover, new_doc, start_story
from k8s_content_a import day1, day2, day3, day4, day5, front_matter
from k8s_content_b import closing, day6, day7, day8, day9, day10
from k8s_content_c import day11
from reportlab.platypus import PageBreak

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kubernetes")

DAYS = [
    (1, "Why Kubernetes and Architecture", "Why-Kubernetes-Architecture", day1),
    (2, "Pods, YAML and kubectl", "Pods-YAML-kubectl", day2),
    (3, "ReplicaSets and Deployments", "Deployments-Rollouts", day3),
    (4, "Services and Networking", "Services-Networking", day4),
    (5, "Ingress, Gateway API and Namespaces", "Ingress-Namespaces", day5),
    (6, "ConfigMaps and Secrets", "ConfigMaps-Secrets", day6),
    (7, "Storage and StatefulSets", "Storage-StatefulSets", day7),
    (8, "Workloads and Scheduling", "Workloads-Scheduling", day8),
    (9, "Health, Autoscaling and Troubleshooting", "Health-Autoscaling-Troubleshooting", day9),
    (10, "Security, GitOps and Production", "Security-GitOps-Production", day10),
    (11, "Helm Charts, Kustomize and Cluster Essentials", "Helm-Kustomize-Cluster-Essentials", day11),
]

BOOK_NAME = "Kubernetes-11-Day-Course.pdf"
OLD_OUTPUTS = ["Kubernetes-10-Day-Course.pdf", "Kubernetes-Class-10-Security-Helm-Production.pdf"]

BOOK_CHIPS = ["Architecture", "Pods", "Deployments", "Services", "Ingress", "ConfigMaps & Secrets",
              "Storage", "StatefulSets", "Scheduling", "Probes & HPA", "RBAC", "GitOps", "Helm charts",
              "Kustomize", "20 interview Q&A per class"]


def build_book():
    out = os.path.join(OUT_DIR, BOOK_NAME)
    cover = draw_cover("Kubernetes\nfor Freshers", "Complete 11-class course with live labs",
                       "Follow Ravi at QuickBite from his first pod to production", BOOK_CHIPS)
    doc = new_doc(out, "Kubernetes for Freshers - 11-Class Course", "Kubernetes training notes", cover)
    story = start_story() + front_matter()
    for _, _, _, fn in DAYS:
        story += [PageBreak()] + fn()
    story += [PageBreak()] + closing()
    doc.multiBuild(story)
    return out


def build_day(num, title, slug, fn):
    out = os.path.join(OUT_DIR, f"Kubernetes-Class-{num:02d}-{slug}.pdf")
    cover = draw_cover(f"Kubernetes\nClass {num}", title,
                       "Student notes - concepts, diagrams, live lab and 20 interview questions",
                       ["60-90 minutes", "Everyday examples", "Diagrams", "Live lab", "20 interview Q&A"])
    doc = new_doc(out, f"Kubernetes Class {num} - {title}", "Kubernetes training notes", cover)
    doc.multiBuild(start_story() + fn())
    return out


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in OLD_OUTPUTS:
        old = os.path.join(OUT_DIR, name)
        if os.path.exists(old):
            os.remove(old)
    paths = [build_book()]
    for num, title, slug, fn in DAYS:
        paths.append(build_day(num, title, slug, fn))
    return paths


if __name__ == "__main__":
    for p in build():
        print(p)
